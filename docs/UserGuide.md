# Shepherd User Guide

## Shepherd URLs:

- Dev: https://shepherd-dev.topsites.nonprod.cloudops.mozgcp.net/admin
- Stage: https://shepherd-stage.topsites.nonprod.cloudops.mozgcp.net/admin/
- Prod: https://shepherd.services.mozilla.com/admin/

## Access Requirements

1. Shepherd Google Access Group
   *  Not being part of the group would result in a Google access denied warning when attempting visiting any of the Shepherd URLs
2. Shepherd Django Roles
   * Not having these roles would result in being presented the "Django Administration" login page
   
*For access please ask someone on the Engineering Team. For engineers, ask to be given superuser privileges. For ad operations ask to be added to the 'AdOps' Django group*

## Using Shepherd

### Adding Partners
This is restricted to the Content Discovery Engineering team. 
From the main admin page, under the Contile subsection click the 
add Partners button. Type in name of partner and click save.

### Adding Advertisers
From the main admin page under the Contile subsection:
1. Click the Add Advertisers Button. 
2. Fill in the info required. 
   * For adding more URLs for an advertiser, there is a green “+” 
   under the Geo group dropdown. 
3. Click “Save” once you’re done. 
   * Red text will appear around certain textboxes if the value violates validation requirements. 
      Correct them and hit save again. 
   * A successful save will have a green bar near the top of the page that says so.

### Creating and Publishing a Snapshot
Click the Add buttons for Settings snapshots under CONSVC_SHEPHERD:

1. Input a name 
   * recommendation is to have the name relate to the changes done to the advertiser (ex. Added Advertiser X Y and Z or Added Black Friday URLs to X) The name has a 128 Character limit.
2. Select settings type. At this time, this would be the Partner name.
3. Hit Save. A Snapshot has been saved. 
4. To publish it, click the checkbox that corresponds to the snapshot. 
5. Select “Publish Settings Snapshot” from the actions dropdown and click “Go”.
   * A green status bar should appear at the top of the page stating the snapshot has been published.

*Note that Shepherd is unable to undo snapshots. 
If changes need to be undone, one would have to manually revert the advertiser information and create a new snapshot.
For complex reverts, please contact the engineering team.*
