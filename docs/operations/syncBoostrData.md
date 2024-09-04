# Sync data from Boostr and upsert it into the Shepherd DB

Currently this is a Django admin command that can be manually run by `docker exec`-ing into a shepherd app container. This job is ran regularly by the Kubernetes cron schedule documented in [SyncBoostrDataCron.md](syncBoostrDataCron.md)

### Instructions to run

1. Find the credentials for the Boostr API in the 1Password vault
2. Set the credentials by copying .env.example to .env, and setting the BOOSTR_API_EMAIL and BOOSTR_API_PASS variables
3. Exec into the consvc-shepherd container:

```sh
docker exec -it consvc-shepherd-app-1 sh
```
4. Find the base url of the Boostr API that you want to hit. For production Boostr, this is "https://app.boostr.com/api/".
5. Run the script, providing base url as a positional arg.
```sh
python manage.py sync_boostr_data https://app.boostr.com/api/
```

### Optional arguments

The script can take an optional named argument, `--max-deal-pages`, which will
set an upper limit on the number of pages of deals that we fetch from the API.

By default, the script will fetch pages of 300 deals at a time until it
receives an empty response from the Boostr API. And if it never receives an
empty response, the script will stop fetching after 50 deal pages by default
(`MAX_DEAL_PAGES_DEFAULT`).

We currently have about 14 pages of deals (at 300 deals per page) in our
production Boostr account, so the default value of 50 gives us lots of overhead,
but this parameter allows us to invoke the script with a custom value for the
upper limit on deal pages.

Usage:
```sh
python manage.py sync_boostr_data
```

### Debug logs

The script takes several minutes to run. To get more detailed logging on which
specific deals and products are being saved, run with `SHEPHERD_ENV=DEBUG`

```shell
SHEPHERD_ENV=DEBUG python manage.py sync_boostr_data
```
