# Sync data from BigQuery and upsert it into the Shepherd DB

Currently this is a Django admin command that can be manually run by `docker exec`-ing into a shepherd app container. This job is ran regularly by the Kubernetes cron schedule documented in [SyncBigQueryDataCron.md](./syncBigQueryDataCron.md)

### Instructions to run

1. Ensure that your LDAP email has [Cat Ads 2](https://mozilla-hub.atlassian.net/wiki/spaces/MA1/pages/575897693/Ads+Sensitive+Data+Policy) level access. This is necessary because BigQuery queries grant us access to sensitive data (e.g., ad partner information, revenue data, etc.). Without the proper permissions, querying the database view below will not work.
    1. If you do not have permission, request it by filling out the [Ads Data Access Request](https://mozilla-hub.atlassian.net/servicedesk/customer/portal/14/create/1315) form.
1. Make sure you have the `PROJECT_ID` set in your `.env` file. For local development, we use the ads nonprod GCP project ID `moz-fx-ads-nonprod`.
1. Login to gcloud locally with `gcloud auth application-default login`.
1. Copy your gcloud creds into the shepherd container:
    ```
    docker cp ~/.config/gcloud/application_default_credentials.json consvc-shepherd-app-1:/app/application_default_credentials.json
    ```
1. Exec into the `consvc-shepherd-app-1` container:
    ```sh
    make debug
    ```
1. Export the gcloud credentials as an env variable:
    ```sh
    export GOOGLE_APPLICATION_CREDENTIALS="/app/application_default_credentials.json"
    ```
1. Run the script for today's date:
    ```sh
    python manage.py sync_bq_data --date $(date +%F)
    ```

### Optional arguments

#### --date

The script accepts an optional named argument, --date, which can be used to
fetch queries for any day. Ensure that the date is in the format YYYY-MM-DD.

By default, the script will use today's date.