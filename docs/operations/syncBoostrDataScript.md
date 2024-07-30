## Sync data from Boostr and upsert it into the Shepherd DB

Currently this is a manual script that can be run by `docker exec`-ing into a container. The intention is that this will become a regularly running job soon.

### Instructions to run

1. Exec into the consvc-shepherd container:
  ```sh
    docker exec -it consvc-shepherd-app-1 sh
  ```
2. Find the credentials for the Boostr API in the 1Password vault
3. Find the base url of the Boostr API that you want to hit. For production Boostr, this is "https://app.boostr.com/api/".
4. Run the script, providing the credentials and base url as environment variables:
```sh
python manage.py sync_boostr_data https://app.boostr.com/api/ find-me-in-1pass@mozilla.com find-me-in-1pass
```

### Notes

The script takes several minutes to run. To get more detailed logging on which specific deals and products are being saved, run with `SHEPHERD_ENV=DEBUG`

```shell
SHEPHERD_ENV=DEBUG python manage.py sync_boostr_data https://app.boostr.com/api/ find-me-in-1pass@mozilla.com find-me-in-1pass
```
