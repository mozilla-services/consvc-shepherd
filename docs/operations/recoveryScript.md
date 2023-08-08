## Recover Snapshot

The script is used as a last resort to revert data in Shepherd back to a specific snapshot.
You would need to:

1. Log into Shepherd Admin as a superuser.
1. Delete the partner model instance which will also delete all its child instances.
1. Run `python3 main.py <SHEPHERD URL> <PATH TO JSON FILE> <PATH TO FIREFOX PROFILE>`
This will add advertisers and advertiser urls based on the values from the
json file you provide it.