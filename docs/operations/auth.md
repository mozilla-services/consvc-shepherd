## Authorization and Access Requirements

There are a number of authorization and access requirements needed to be able to access Shepherd.

1. Shepherd Google Access Group
   *  Not being part of the group would result in a Google access denied warning when attempting visiting any of the Shepherd URLs.
2. Shepherd Django Roles
   * Not having these roles would result in being presented the "Django Administration" login page.
   * You can create a new admin user though the Users panel in Django Admin.
   
*For access please ask someone on the Engineering Team. For engineers, ask to be given superuser privileges. For ad operations ask to be added to the 'AdOps' Django group*

## Shepherd URLs:

- Stage: https://shepherd.stage.ads.nonprod.webservices.mozgcp.net/admin/
- Prod: https://shepherd.services.mozilla.com/admin/
