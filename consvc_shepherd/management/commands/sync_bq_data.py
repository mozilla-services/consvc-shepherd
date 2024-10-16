"""Django admin custom command for fetching ad data from BigQuery and saving it to Shepherd DB"""

import logging
import traceback
from datetime import datetime

import pandas
from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.utils import timezone
from google.cloud import bigquery

from consvc_shepherd.models import BQSyncStatus, DeliveredFlight

SYNC_STATUS_SUCCESS = "success"
SYNC_STATUS_FAILURE = "failure"
DEFAULT_PROJECT_ID = "moz-fx-ads-prod"


class Command(BaseCommand):
    """Django admin custom command for fetching ad data from BigQuery and saving it to Shepherd DB"""

    help = "Run a script that fetches ad data from BigQuery and stores it in Shepherd"

    def add_arguments(self, parser):
        """Register expected command line arguments"""
        parser.add_argument(
            "--project_id",
            default=DEFAULT_PROJECT_ID,
            type=str,
            help='The GCP project ID that will interact with BQ. By default, it will use "moz-fx-ads-prod"',
        )
        parser.add_argument(
            "--date",
            default=datetime.today().strftime("%Y-%m-%d"),
            type=str,
            help="The date we want to capture metrics for, e.g. 2024-09-18. By default, it will use today's date.",
        )

    def handle(self, *args, **options):
        """Handle running the command"""
        self.stdout.write(f"Starting BigQuery sync for date {options['date']}")

        try:
            datetime.strptime(options["date"], "%Y-%m-%d")
        except ValueError:
            raise CommandError("Invalid date format. Please use YYYY-MM-DD")

        try:
            bigquery.Client(project=options["project_id"])
        except Exception as e:
            raise CommandError(
                f"Invalid project ID: {options['project_id']}. Error: {e}"
            )

        syncer = BQSyncer(options["project_id"], options["date"])

        try:
            syncer.sync_data()
        except Exception as e:
            raise CommandError(f"{e}")

        self.stdout.write(f"BigQuery sync completed for date {options['date']}")


class NoDataReturnedError(Exception):
    """Exception raised when no data is returned from the BigQuery query."""

    def __init__(self, date: str):
        self.message = f"No data returned for date {date}"
        super().__init__(self.message)


class BQSyncer:
    """Wrap up interaction with BigQuery"""

    log: logging.Logger
    project_id: str
    date: str

    def __init__(self, project_id: str, date: str):
        self.log = logging.getLogger("sync_bigquery_ads_data")
        self.project_id = project_id
        self.date = date

    def query_bq(self) -> pandas.DataFrame:
        """Create SQL query, send query BQ through its client"""
        query = """
            SELECT
                submission_date,
                campaign_id,
                campaign_name,
                flight_id,
                flight_name,
                provider,
                SUM(clicks) AS clicks,
                SUM(impressions) AS impressions
            FROM
                `moz-fx-data-shared-prod.ads.consolidated_ad_metrics_daily_pt`
            WHERE
                submission_date = @submission_date
                AND flight_id IS NOT NULL
                AND campaign_id IS NOT NULL
            GROUP BY
                submission_date,
                campaign_id,
                campaign_name,
                flight_id,
                flight_name,
                provider
        """

        client = bigquery.Client(project=self.project_id)

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("submission_date", "DATE", self.date)
            ]
        )

        try:
            query_job = client.query(query, job_config=job_config)
            results = query_job.result()

            if results.total_rows == 0:
                raise NoDataReturnedError(self.date)

            df = results.to_dataframe()

            self.log.info(f"BQ data pulled successfully for date {self.date}")
            return df
        except Exception as e:
            self.log.error(f"An error occurred while querying BigQuery: {e}")
            raise  # Re-raise the exception to propagate it further

    def upsert_data(self, df):
        """Upsert data queried from BigQuery into Shepherd DB"""
        for _, row in df.iterrows():
            submission_date = row["submission_date"]
            campaign_id = row["campaign_id"]
            campaign_name = row["campaign_name"]
            flight_id = row["flight_id"]
            flight_name = row["flight_name"]
            provider = row["provider"]
            clicks = row["clicks"]
            impressions = row["impressions"]

            delivered_flight, created = DeliveredFlight.objects.update_or_create(
                submission_date=submission_date,
                campaign_id=campaign_id,
                campaign_name=campaign_name,
                flight_id=flight_id,
                flight_name=flight_name,
                provider=provider,
                defaults={
                    "clicks_delivered": clicks,
                    "impressions_delivered": impressions,
                },
            )

            if created:
                self.log.info(f"Created new DeliveredFlight: {delivered_flight}")
            else:
                self.log.info(f"Updated DeliveredFlight: {delivered_flight}")

    def update_sync_status(self, status: str, message: str):
        """Update the BQSyncStatus table given the status and the message"""
        query_date = datetime.strptime(self.date, "%Y-%m-%d")
        query_date = timezone.make_aware(query_date)
        BQSyncStatus.objects.create(
            status=status,
            message=message,
            synced_on=timezone.now(),
            query_date=query_date,
        )

    def sync_data(self):
        """BQ Syncer entrypoint"""
        try:
            df = self.query_bq()

            if not df.empty:
                self.upsert_data(df)

            self.log.info(
                "BigQuery sync process has completed successfully. Updating sync_status"
            )
            self.update_sync_status(SYNC_STATUS_SUCCESS, "BigQuery sync success")
        except NoDataReturnedError as e:
            self.update_sync_status(SYNC_STATUS_FAILURE, str(e))
            raise e
        except Exception as e:
            error = (
                f"Exception: {SYNC_STATUS_FAILURE}, query date: {self.date}, {str(e)} "
                f"Trace: {traceback.format_exc()}"
            )
            self.update_sync_status(SYNC_STATUS_FAILURE, error)
            raise e
