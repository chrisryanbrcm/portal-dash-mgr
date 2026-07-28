# PRODUCT NAME: NetOps Portal Dashboard Manager
# DESIGN CONSIDERATIONS

This file defines different aspects of this web application. It is not an official design or architecture document.

## REFERENCE DOCUMENTATION

The technical documentation related to this specific functionality can be found here: https://techdocs.broadcom.com/us/en/ca-enterprise-software/it-operations-management/dx-netops/25-4/Performance-Monitoring-with-DX-Performance-Management/apis/performance-center-rest-web-services/dashboards-web-service.html

## UI

EXPORT FUNCTION Must Haves:
- Primary Functions
    - Export Dashboard interface
    - Import Dashboard interface
- Ignore SSL Verification checkbox
- URL field
    - Consider using the actual URL and converting it to the RestAPI call
- Port field defaulted to 8181
    - Consider a dropdown with options: 8181, 443, Custom (where the user can type a port number)
    - Consider automatically populating the port # by pulling it from the pasted URL in the URL field
- Authentication
    - Basic (with fields for username, password)
    - Token (with field to paste token)
    - None
- Text field for parsing out the Dashboard ID (paste existing web URL and extract/display pg=)
    - Automatically populate, but allow it to be editable
- Status Code (e.g. 200 OK, 404 Not Found)
- Response
    - Show the XML response
- Save Dashboard to File button
- Reminder Message on Export/Save of the following:
    - Before using the file for import, update the menu items to identify where it should be exist in the new NetOps Portal menu hierarchy
        - <menuItem>: Defines which menu group the dashboard will attach to (e.g., <menuItem>Custom Dashboards</menuItem>).
        - <dashboardTitle>: Specifies the display name of the imported dashboard.
        
            Note: If a dashboard with the exact same <dashboardTitle> already exists on the target server, rename the text inside <dashboardTitle> in your XML body before importing to avoid name collision errors.

        See https://techdocs.broadcom.com/us/en/ca-enterprise-software/it-operations-management/dx-netops/25-4/Performance-Monitoring-with-DX-Performance-Management/apis/performance-center-rest-web-services/dashboards-web-service.html for more information.



IMPORT FUNCTION Must Haves:
- Ignore SSL Verification checkbox
- URL field
    - Consider using the actual URL and converting it to the RestAPI call
- Port field defaulted to 8181
    - Consider a dropdown with options: 8181, 443, Custom (where the user can type a port number)
    - Consider automatically populating the port # by pulling it from the pasted URL in the URL field
- Authentication
    - Basic (with fields for username, password)
    - Token (with field to paste token)
    - None
- Upload File
    - Define the XML file that will be used to POST to the target Portal RestAPI
    - Display the XML file contents in a view-only text box
        - Extract the <dashboardMenu>, <menuItem>, and <dashboardTitle> contents and display them above this text box
- Reminder Message on "Save" to confirm that the XML properly reflects the target menu hierarchy ("CONTINUE/CANCEL")
- Status Code (e.g. 200 OK, 404 Not Found)
- Contain text that identifies the process to add & define new menus in NetOps Portal
    - Step 1: Create the New Menu
        1.1 Log in to NetOps Portal as a user with administrative or designer rights.
    
        1.2 In the top navigation bar, go to Administration > User Settings > Menus.

        1.3 On the Manage Menus page, click New.

        1.4 In the Add Menu dialog:

            Menu Name: Enter a display title for your custom menu.

            Description: Add an optional description.

            Add Dashboards: Select dashboards from the Available Dashboards list and click the Select item arrow to move them into the Selected Dashboards list.

        1.5 Click Save.

    - Step 2: Associate the Menu with User Roles (Required)
        Important: Creating a menu does not automatically make it visible. You must assign the new menu to a User Role before users with that role can see it in their top navigation bar.

        2.1 Go to Administration > User Settings > Roles.

        2.2 Select the target role (e.g., Network Administrator or a custom role) and click Edit.

        2.3 In the Menus tab/section, locate your newly created menu in the available options.

        2.4 Move the new menu to the Selected Menus column.

        2.5 Click Save.

        Once saved, users belonging to that role will see the new menu and its assigned dashboards listed under the main Performance dropdown tab in the NetOps Portal header.

## TECHNICAL FUNCTIONALITY

EXPORT DASHBOARD
- URL to RestAPI address
- Option to disable SSL verification
- Perform a GET on the URL and display formatted XML, export to a file
- Identify Dashboard ID (pg=) from pasted URL
- Define or auto-populate a port
- Authentication
    - Support Basic Auth and Bearer Token
- Header must be "Content Type: application/xml"

IMPORT DASHBOARD
- URL for target Portal server which 
- Perform a POST on a target URL using an XML file from the local computer