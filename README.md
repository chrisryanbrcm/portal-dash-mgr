# NetOps Portal Dashboard Manager

A lightweight web tool for exporting dashboards from one DX NetOps Portal server and importing them into another, without needing to hand-craft REST calls. It wraps the Portal's dashboard web service in a simple browser UI: paste a dashboard URL to export its XML, or upload an XML file to import it into a target server — with authentication, SSL, and menu-hierarchy checks built in.

## Features

**Export Dashboard**
- Paste a Portal dashboard URL; the app auto-extracts the host, port, and dashboard ID (`pg=`) from it
- Port is editable (dropdown: `8181`, `443`, or Custom)
- Authentication: None, Basic (username/password), or Token (bearer)
- Optional "Ignore SSL Verification" for self-signed Portal certificates
- Displays the HTTP status code and the pretty-printed XML response
- "Save Dashboard to File" downloads the XML — a confirmation modal shows the detected `<menuItem>` and `<dashboardTitle>` values and reminds you to update them before importing elsewhere, to avoid menu placement or title-collision errors

**Import Dashboard**
- Same URL/port/auth/SSL controls as Export, targeting the destination server
- Upload a dashboard XML file; its `<dashboardMenu>`, `<menuItem>`, and `<dashboardTitle>` values are extracted and shown, with a pretty-printed, syntax-highlighted preview of the full file
- A confirmation modal (Continue/Cancel) requires an explicit acknowledgment that the menu hierarchy is correct before the import POST is sent
- Displays the resulting HTTP status code (e.g. `200 OK`, `404 Not Found`)
- Built-in, expandable "NetOps Portal Menu Setup Guide" covering how to create and expose a new menu for imported dashboards

## Technical Stack

- **Backend:** Python 3 / Flask, using `requests` for outbound HTTP calls and `lxml` for XML pretty-printing
- **Frontend:** Server-rendered HTML (`templates/index.html`) styled with Tailwind CSS (via CDN) and plain JavaScript (no build step, no frontend framework)
- **Packaging:** Docker, orchestrated with Docker Compose

## Project Structure

```
app.py                  Flask app: routes, URL parsing, and Portal API proxy logic
templates/index.html    Single-page UI (Export/Import tabs)
requirements.txt        Python dependencies
Dockerfile              Container image definition
docker-compose.yml      Local/deployment orchestration (port 5000)
DESIGN.md               Product/UI specification
```

## Deployment

Requires Docker and Docker Compose.

```bash
docker compose up -d --build
```

The app is then available at `http://localhost:5000`. Check container health with:

```bash
curl http://localhost:5000/health
```

To stop it:

```bash
docker compose down
```

### Running locally without Docker

```bash
pip install -r requirements.txt
python app.py
```

## API Reference

### App endpoints (this service)

| Method | Path              | Description                                                        |
|--------|-------------------|----------------------------------------------------------------------|
| GET    | `/health`         | Health check, returns `{"status": "ok"}`                             |
| GET    | `/`                | Serves the UI                                                       |
| POST   | `/api/export`      | Fetches a dashboard's XML from a NetOps Portal server               |
| POST   | `/api/import`       | Posts a dashboard's XML to a target NetOps Portal server            |
| POST   | `/api/format-xml`  | Pretty-prints arbitrary XML (used for the Import preview)          |

`/api/export` request body:
```json
{
  "url": "https://netops.example.com:8181/dashboard/content/index.html#/dashboard?pg=42",
  "port": "8181",
  "page_id": "42",
  "auth_type": "basic | token | none",
  "username": "...",
  "password": "...",
  "token": "...",
  "ignore_ssl": false
}
```
`port` and `page_id` are optional — if omitted they're derived from `url`. Response: `{"status_code": 200, "target_url": "...", "xml": "..."}`.

`/api/import` request body:
```json
{
  "url": "https://netops.example.com:8181/",
  "port": "8181",
  "auth_type": "basic | token | none",
  "username": "...",
  "password": "...",
  "token": "...",
  "ignore_ssl": false,
  "xml": "<dashboardMenu>...</dashboardMenu>"
}
```
Response: `{"status_code": 200, "reason": "OK", "target_url": "..."}`.

### Underlying NetOps Portal REST calls

This tool is a thin client over the Portal's dashboard web service ([full documentation](https://techdocs.broadcom.com/us/en/ca-enterprise-software/it-operations-management/dx-netops/25-4/Performance-Monitoring-with-DX-Performance-Management/apis/performance-center-rest-web-services/dashboards-web-service.html)):

**Export** — `GET {protocol}://{host}:{port}/pc/center/webservice/dashboards/{page_id}`
Header: `Accept: application/xml`

**Import** — `POST {protocol}://{host}:{port}/pc/center/webservice/dashboards/import`
Header: `Content-Type: application/xml`
Body: the dashboard XML document

Both calls support HTTP Basic Auth or a Bearer token in the `Authorization` header, and can skip TLS certificate verification for servers using self-signed certificates.

## User Permissions & Menu Setup in NetOps Portal

Exporting and importing dashboards via this API requires a NetOps Portal account with **administrative or designer rights** on both the source and target servers.

Importing a dashboard XML file does **not** automatically place it in a menu that users can see. Before importing, check the file's `<menuItem>` and `<dashboardTitle>` values (the app surfaces these to you at export- and import-time) and, on the target server:

1. **Create the menu** (if it doesn't already exist): *Administration > User Settings > Menus > New*, give it a name, and add the relevant dashboards to it.
2. **Associate the menu with a user role**: *Administration > User Settings > Roles*, edit the target role, and move the new menu into its Selected Menus. This step is required — a menu isn't visible to any user until it's assigned to their role.

The in-app "NetOps Portal Menu Setup Guide" accordion on the Import tab walks through both steps in full detail.

## Security Notes

- This tool has no built-in authentication of its own — it's intended for trusted, internal use.
- The "Ignore SSL Verification" option disables TLS certificate checking for the target Portal request; only use it against servers you trust (e.g. internal servers with self-signed certs).
- Credentials entered in the UI are sent directly to the target Portal server and are not persisted by this app.
