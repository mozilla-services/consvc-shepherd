"""Unit tests for the sync_bq_data command"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class TestBQSyncerData(TestCase):
    """Unit tests for functions that fetch from BigQuery and store in our DB"""

    @patch(
        "consvc_shepherd.management.commands.sync_bq_data.DeliveredFlight.objects.update_or_create"
    )
    @patch("consvc_shepherd.management.commands.sync_bq_data.BQSyncer.query_bq")
    @patch("consvc_shepherd.management.commands.sync_bq_data.bigquery.Client")
    @patch(
        "consvc_shepherd.management.commands.sync_bq_data.BQSyncer.update_sync_status"
    )
    def test_sync_data_successful(
        self,
        mock_update_sync_status,
        mock_bigquery_client,
        mock_query_bq,
        mock_update_or_create,
    ):
        """Test that sync_data inserts data into DB when BQ query is successful"""
        mock_query_job = MagicMock()
        mock_query_job.result.return_value.total_rows = 1
        mock_query_job.result.return_value.to_dataframe.return_value = pd.DataFrame(
            {
                "submission_date": ["2024-09-18"],
                "campaign_id": [1],
                "campaign_name": ["Campaign 1"],
                "flight_id": [100],
                "provider": ["Provider 1"],
                "clicks": [10],
                "impressions": [100],
            }
        )

        mock_query_bq.return_value = mock_query_job.result.return_value.to_dataframe()
        mock_bigquery_client.return_value.query.return_value = mock_query_job
        mock_update_or_create.return_value = (MagicMock(), True)

        with self.assertLogs("sync_bigquery_ads_data", level="INFO") as log:
            call_command("sync_bq_data", project_id="test-project", date="2024-09-18")

        mock_query_bq.assert_called_once()

        mock_update_or_create.assert_called_once_with(
            submission_date="2024-09-18",
            campaign_id=1,
            campaign_name="Campaign 1",
            flight_id=100,
            provider="Provider 1",
            defaults={
                "clicks_delivered": 10,
                "impressions_delivered": 100,
            },
        )

        self.assertIn("Created new DeliveredFlight", log.output[0])

        self.assertIn(
            "BigQuery sync process has completed successfully. Updating sync_status",
            log.output[1],
        )

        mock_update_sync_status.assert_called_once_with(
            "success", "2024-09-18", "BigQuery sync success"
        )

    @patch("consvc_shepherd.management.commands.sync_bq_data.BQSyncer.sync_data")
    @patch("consvc_shepherd.management.commands.sync_bq_data.bigquery.Client")
    def test_sync_data_failure(self, mock_bigquery_client, mock_sync_data):
        """Test sync_data logs errors accordingly when it can't insert into shepherd DB"""
        mock_sync_data.side_effect = Exception(
            "An error occurred while querying BigQuery"
        )

        mock_bigquery_client.return_value = MagicMock()

        with self.assertRaises(CommandError) as context:
            call_command("sync_bq_data", project_id="test-project", date="2024-09-18")

        self.assertIn(
            "An error occurred while querying BigQuery",
            str(context.exception),
        )

    @patch(
        "consvc_shepherd.management.commands.sync_bq_data.DeliveredFlight.objects.update_or_create"
    )
    @patch("consvc_shepherd.management.commands.sync_bq_data.BQSyncer.query_bq")
    @patch("consvc_shepherd.management.commands.sync_bq_data.bigquery.Client")
    @patch(
        "consvc_shepherd.management.commands.sync_bq_data.BQSyncer.update_sync_status"
    )
    def test_sync_data_multiple_rows(
        self,
        mock_update_sync_status,
        mock_bigquery_client,
        mock_query_bq,
        mock_update_or_create,
    ):
        """Test that sync_data processes multiple rows returned from BigQuery"""
        mock_query_job = MagicMock()
        mock_query_job.result.return_value.total_rows = 2
        mock_query_job.result.return_value.to_dataframe.return_value = pd.DataFrame(
            {
                "submission_date": ["2024-09-18", "2024-09-18"],
                "campaign_id": [1, 2],
                "campaign_name": ["Campaign 1", "Campaign 2"],
                "flight_id": [100, 101],
                "provider": ["Provider 1", "Provider 2"],
                "clicks": [10, 20],
                "impressions": [100, 200],
            }
        )

        mock_query_bq.return_value = mock_query_job.result.return_value.to_dataframe()
        mock_bigquery_client.return_value.query.return_value = mock_query_job

        mock_update_or_create.return_value = (MagicMock(), True)

        with self.assertLogs("sync_bigquery_ads_data", level="INFO") as log:
            call_command("sync_bq_data", project_id="test-project", date="2024-09-18")

        mock_query_bq.assert_called_once()

        self.assertEqual(mock_update_or_create.call_count, 2)

        self.assertIn("Created new DeliveredFlight", log.output[0])

        self.assertIn("Created new DeliveredFlight", log.output[1])

        self.assertIn(
            "BigQuery sync process has completed successfully. Updating sync_status",
            log.output[2],
        )

        mock_update_sync_status.assert_called_once_with(
            "success", "2024-09-18", "BigQuery sync success"
        )

    @patch("consvc_shepherd.management.commands.sync_bq_data.BQSyncer.query_bq")
    @patch("consvc_shepherd.management.commands.sync_bq_data.bigquery.Client")
    @patch(
        "consvc_shepherd.management.commands.sync_bq_data.DeliveredFlight.objects.update_or_create"
    )
    def test_sync_data_default_date(
        self, mock_update_or_create, mock_bigquery_client, mock_query_bq
    ):
        """Test the sync_bq_data command without a date argument defaults to today's date."""
        mock_query_job = MagicMock()
        mock_query_job.result.return_value.total_rows = 1
        mock_query_job.result.return_value.to_dataframe.return_value = pd.DataFrame(
            {
                "submission_date": [
                    datetime.today().strftime("%Y-%m-%d")
                ],  # Today's date
                "campaign_id": [1],
                "campaign_name": ["Campaign 1"],
                "flight_id": [100],
                "provider": ["Provider 1"],
                "clicks": [10],
                "impressions": [100],
            }
        )

        mock_query_bq.return_value = mock_query_job.result.return_value.to_dataframe()
        mock_bigquery_client.return_value.query.return_value = mock_query_job
        mock_update_or_create.return_value = (MagicMock(), True)

        call_command("sync_bq_data", project_id="test-project")

        mock_query_bq.assert_called_once()

        mock_update_or_create.assert_called_once_with(
            submission_date=datetime.today().strftime("%Y-%m-%d"),
            campaign_id=1,
            campaign_name="Campaign 1",
            flight_id=100,
            provider="Provider 1",
            defaults={
                "clicks_delivered": 10,
                "impressions_delivered": 100,
            },
        )

    @patch(
        "consvc_shepherd.management.commands.sync_bq_data.DeliveredFlight.objects.update_or_create"
    )
    @patch("consvc_shepherd.management.commands.sync_bq_data.bigquery.Client")
    def test_no_data_returned_for_date(
        self, mock_bigquery_client, mock_update_or_create
    ):
        """Test the command raises an error if BigQuery doesn't return data for a given date"""
        mock_query_job = MagicMock()
        mock_query_job.result.return_value.total_rows = 0
        mock_query_job.result.return_value.to_dataframe.return_value = pd.DataFrame()

        mock_bigquery_client.return_value.query.return_value = mock_query_job

        with self.assertRaises(CommandError) as context:
            call_command("sync_bq_data", project_id="test-project", date="2024-09-18")

        self.assertIn("No data returned for date 2024-09-18", str(context.exception))
        mock_update_or_create.assert_not_called()

    @patch("consvc_shepherd.management.commands.sync_bq_data.bigquery.Client")
    def test_invalid_project_id(self, mock_bigquery_client):
        """Test the command raises an error for an invalid project ID"""
        mock_bigquery_client.side_effect = Exception("Invalid project ID")

        with self.assertRaises(CommandError) as context:
            call_command(
                "sync_bq_data", project_id="invalid_project_id", date="2024-09-18"
            )

        self.assertIn("Invalid project ID: invalid_project_id", str(context.exception))
