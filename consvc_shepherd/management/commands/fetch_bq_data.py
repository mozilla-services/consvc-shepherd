"""Django admin custom command for fetching ad data from BigQuery and saving it to Shepherd DB"""

import logging
import traceback
from datetime import datetime

import pandas
from django.core.management import CommandError
from django.core.management.base import BaseCommand
from google.cloud import bigquery

from consvc_shepherd.models import DeliveredFlight


class Command(BaseCommand):
    """Django admin custom command for fetching ad data from BigQuery and saving it to Shepherd DB"""

    help = "Run a script that fetches ad data from BigQuery and stores it in Shepherd"

    def add_arguments(self, parser):
        """Register expected command line arguments"""
        parser.add_argument(
            "--project_id",
            type=str,
            help="The GCP project ID that will interact with BQ, e.g. moz-fx-ads-nonprod.",
        )
        parser.add_argument(
            "--date",
            default=datetime.today().strftime("%Y-%m-%d"),
            type=str,
            help="The date we want to capture metrics for, e.g. 2024-09-18. By default, it will use today's date.",
        )

    def handle(self, *args, **options):
        """Handle running the command"""
        self.stdout.write(f"Starting BigQuery fetch for date {options['date']}")

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

        fetcher = BQFetcher(options["project_id"], options["date"])

        try:
            fetcher.fetch_data()
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")

        self.stdout.write(f"BigQuery fetch completed for date {options['date']}")


class BQFetcher:
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
                message = f"No data returned for the date {self.date}"
                self.log.error(message)
                raise ValueError(message)

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
                # If script runs again in the same day, just update the clicks and impressions
                defaults={
                    "clicks_delivered": clicks,
                    "impressions_delivered": impressions,
                },
            )

            if created:
                self.log.info(f"Created new DeliveredFlight: {delivered_flight}")
            else:
                self.log.info(f"Updated DeliveredFlight: {delivered_flight}")

    def fetch_data(self):
        """BQ Fetcher entrypoint"""
        try:
            df = self.query_bq()

            self.upsert_data(df)
            self.log.info("BigQuery fetcher process has completed successfully")
        except ValueError as ve:
            self.log.warning(f"No data returned for the date {self.date}: {str(ve)}")
            return  # Exit early if no data is present
        except Exception as e:
            error = f"Exception: {str(e):} Trace: {traceback.format_exc()}"
            self.log.error(f"BigQuery fetcher process has encounterd an error: {error}")
            raise
