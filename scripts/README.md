# Scripts

## recover.py

Precondition: Be able to log into Shepherd Admin as a superuser.

The script is used as a last resort to revert data in Shepherd back to a specific snapshot.
One would need to:
1. delete the partner model instance which will also delete all its child instances.
Once that is completed, the script can be used. 

2. Run `python3 main.py <SHEPHERD URL> <PATH TO JSON FILE> <PATH TO FIREFOX PROFILE>`
This will add advertisers and advertiser urls based on the values from the
json file you provide it.