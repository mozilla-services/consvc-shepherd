"""Django admin custom command for fetching ad data from BigQuery and saving it to Shepherd DB"""

import logging
import traceback
from datetime import datetime

import pandas
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from google.cloud import bigquery

from consvc_shepherd.models import Campaign, DeliveredCampaign


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
            self.stderr.write("Invalid date format. Please use YYYY-MM-DD")
            return

        fetcher = BQFetcher(options["project_id"], options["date"])

        fetcher.fetch_data()

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
                flight_id,
                provider,
                country,
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
                flight_id,
                country,
                provider
        """

        client = bigquery.Client(project=self.project_id)

        # Configure the query with the required parameter (the date entered)
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("submission_date", "DATE", self.date)
            ]
        )

        try:
            # Execute the query
            query_job = client.query(query, job_config=job_config)
            results = query_job.result()

            if results.total_rows == 0:
                raise ValueError(f"No data returned for the date {self.date}")

            # Convert results to DataFrame
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
            flight_id = row["flight_id"]
            country = row["country"]
            provider = row["provider"]
            clicks = row["clicks"]
            impressions = row["impressions"]

            try:
                campaign = Campaign.objects.get(kevel_flight_id=flight_id)
            except ObjectDoesNotExist:
                self.log.warn(
                    f"Could not find Campaign with kevel_flight_id: {flight_id}. Skipping..."
                )
                continue

            delivered_campaign, created = DeliveredCampaign.objects.update_or_create(
                submission_date=submission_date,
                campaign_id=campaign_id,
                flight=campaign,
                country=country,
                provider=provider,
                # If script runs again in the same day, just update the clicks and impressions
                defaults={
                    "clicks_delivered": clicks,
                    "impressions_delivered": impressions,
                },
            )

            if created:
                self.log.info(f"Created new DeliveredCampaign: {delivered_campaign}")
            else:
                self.log.info(f"Updated DeliveredCampaign: {delivered_campaign}")

    def fetch_data(self):
        """BQ Fetcher entrypoint"""
        try:
            df = self.query_bq()
            self.upsert_data(df)
            self.log.info("BigQuery fetcher process has completed successfully")
        except Exception as e:
            error = f"Exception: {str(e):} Trace: {traceback.format_exc()}"
            self.log.error(f"BigQuery fetcher process has encounterd an error: {error}")
