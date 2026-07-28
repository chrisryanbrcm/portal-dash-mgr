import re
from urllib.parse import urlparse

import requests
import urllib3
from flask import Flask, jsonify, render_template, request
from lxml import etree

# NetOps Portal servers commonly use self-signed certs; suppress the noisy
# InsecureRequestWarning so it doesn't spam logs when a caller disables SSL verification.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

PAGE_ID_PATTERN = re.compile(r"pg=([^&#]+)")


def parse_netops_url(url):
    """Extract protocol, host, port, and dashboard page ID (pg=) from a NetOps Portal URL."""
    parsed = urlparse(url)
    protocol = parsed.scheme or "https"
    port = parsed.port or (443 if protocol == "https" else 80)

    page_id_match = PAGE_ID_PATTERN.search(url)
    page_id = page_id_match.group(1) if page_id_match else None

    return {
        "protocol": protocol,
        "host": parsed.hostname,
        "port": port,
        "page_id": page_id,
    }


def _format_xml(raw_text):
    """Pretty-print XML for display; fall back to raw text (e.g. error pages) if it doesn't parse."""
    try:
        parsed_xml = etree.fromstring(raw_text.encode("utf-8"))
        return etree.tostring(parsed_xml, pretty_print=True, encoding="unicode")
    except etree.XMLSyntaxError:
        return raw_text


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/api/export", methods=["POST"])
def export_dashboard():
    data = request.get_json(silent=True) or {}

    parsed = parse_netops_url(data.get("url", ""))
    host = parsed["host"]
    protocol = parsed["protocol"]
    port = data.get("port") or parsed["port"]
    page_id = data.get("page_id") or parsed["page_id"]

    if not host or not page_id:
        return jsonify({"error": "A valid Portal URL and Dashboard ID (pg=) are required."}), 400

    target_url = f"{protocol}://{host}:{port}/pc/center/webservice/dashboards/{page_id}"

    headers = {"Accept": "application/xml"}
    auth = None
    auth_type = data.get("auth_type", "none")
    if auth_type == "basic":
        auth = (data.get("username", ""), data.get("password", ""))
    elif auth_type == "token":
        headers["Authorization"] = f"Bearer {data.get('token', '')}"

    verify_ssl = not data.get("ignore_ssl", False)

    try:
        response = requests.get(target_url, headers=headers, auth=auth, verify=verify_ssl, timeout=15)
    except requests.exceptions.RequestException as exc:
        return jsonify({"error": str(exc), "target_url": target_url}), 502

    return jsonify({
        "status_code": response.status_code,
        "target_url": target_url,
        "xml": _format_xml(response.text),
    })


@app.route("/api/format-xml", methods=["POST"])
def format_xml():
    data = request.get_json(silent=True) or {}
    return jsonify({"xml": _format_xml(data.get("xml", ""))})


@app.route("/api/import", methods=["POST"])
def import_dashboard():
    data = request.get_json(silent=True) or {}

    parsed = parse_netops_url(data.get("url", ""))
    host = parsed["host"]
    protocol = parsed["protocol"]
    port = data.get("port") or parsed["port"]
    xml = data.get("xml", "")

    if not host or not xml:
        return jsonify({"error": "A valid target URL and an XML file are required."}), 400

    target_url = f"{protocol}://{host}:{port}/pc/center/webservice/dashboards/import"

    headers = {"Content-Type": "application/xml"}
    auth = None
    auth_type = data.get("auth_type", "none")
    if auth_type == "basic":
        auth = (data.get("username", ""), data.get("password", ""))
    elif auth_type == "token":
        headers["Authorization"] = f"Bearer {data.get('token', '')}"

    verify_ssl = not data.get("ignore_ssl", False)

    try:
        response = requests.post(
            target_url, data=xml.encode("utf-8"), headers=headers, auth=auth, verify=verify_ssl, timeout=15
        )
    except requests.exceptions.RequestException as exc:
        return jsonify({"error": str(exc), "target_url": target_url}), 502

    return jsonify({
        "status_code": response.status_code,
        "reason": response.reason,
        "target_url": target_url,
    })


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
