# Scripts

## recover.py

The script is used as a last resort to revert data in Shepherd back to a specific snapshot.
One would need to delete the partner model instance which will also delete all its child instances.
Once that is completed, the script can be used. It will add advertisers and advertiser urls based on the values from the
json file you provide it.