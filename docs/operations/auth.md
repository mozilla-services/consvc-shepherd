## Authorization and Access Requirements

There are a number of authorization and access requirements needed to be able to access Shepherd.

1. Shepherd Google Access Group
   *  Not being part of the group would result in a Google access denied warning when attempting visiting any of the Shepherd URLs
2. Shepherd Django Roles
   * Not having these roles would result in being presented the "Django Administration" login page
   
*For access please ask someone on the Engineering Team. For engineers, ask to be given superuser privileges. For ad operations ask to be added to the 'AdOps' Django group*

## Django Admin

To be able to make changes to settings, you have to be a superuser.  An existing superuser must grant these privileges. 

Locally, to create a superuser,  shell into the Docker container and run the following:
``` shell
docker ps # capture container id for consvc-shepherd
docker exec -it <CONTAINER ID> sh # interactive mode
./manage.py createsuperuser # follow directions to create superuser
```

## Shepherd URLs:

- Dev: https://shepherd-dev.topsites.nonprod.cloudops.mozgcp.net/admin
- Stage: https://shepherd-stage.topsites.nonprod.cloudops.mozgcp.net/admin/
- Prod: https://shepherd.services.mozilla.com/admin/