"""Unit tests for the sync_bq_data command"""

import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from consvc_shepherd.management.commands.sync_bq_data import DeliveredFlight

DEFAULT_PROJECT_ID = "moz-fx-ads-prod"
DEFAULT_DATE = datetime.today().strftime("%Y-%m-%d")


class TestBQSyncerData(TestCase):
    """Unit tests for functions that fetch from BigQuery and store in our DB"""

    @patch.dict(os.environ, {"PROJECT_ID": "test-project"})
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
                "flight_name": ["Flight 1"],
                "provider": ["Provider 1"],
                "clicks": [10],
                "impressions": [100],
            }
        )

        mock_query_bq.return_value = mock_query_job.result.return_value.to_dataframe()
        mock_bigquery_client.return_value.query.return_value = mock_query_job
        mock_update_or_create.return_value = (MagicMock(), True)

        with self.assertLogs("sync_bigquery_ads_data", level="INFO") as log:
            call_command("sync_bq_data", date="2024-09-18")

        mock_query_bq.assert_called_once()

        mock_update_or_create.assert_called_once_with(
            submission_date="2024-09-18",
            campaign_id=1,
            flight_id=100,
            provider="Provider 1",
            defaults={
                "campaign_name": "Campaign 1",
                "flight_name": "Flight 1",
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
            "success", "BigQuery sync success"
        )

    @patch.dict(os.environ, {"PROJECT_ID": "test-project"})
    @patch(
        "consvc_shepherd.management.commands.sync_bq_data.DeliveredFlight.objects.update_or_create"
    )
    @patch("consvc_shepherd.management.commands.sync_bq_data.BQSyncer.sync_data")
    @patch("consvc_shepherd.management.commands.sync_bq_data.bigquery.Client")
    def test_sync_data_failure(
        self, mock_bigquery_client, mock_sync_data, mock_update_or_create
    ):
        """Test that sync_data logs errors and doesn't try to upsert into shepherd DB if BQ query fails"""
        mock_sync_data.side_effect = Exception(
            "An error occurred while querying BigQuery"
        )

        mock_bigquery_client.return_value = MagicMock()

        with self.assertRaises(CommandError) as context:
            call_command("sync_bq_data", date="2024-09-18")

        self.assertIn(
            "An error occurred while querying BigQuery",
            str(context.exception),
        )

        mock_update_or_create.assert_not_called()

    @patch.dict(os.environ, {"PROJECT_ID": "test-project"})
    @patch(
        "consvc_shepherd.management.commands.sync_bq_data.DeliveredFlight.objects.update_or_create"
    )
    @patch("consvc_shepherd.management.commands.sync_bq_data.BQSyncer.query_bq")
    @patch("consvc_shepherd.management.commands.sync_bq_data.bigquery.Client")
    def test_sync_same_flight_updates_clicks_impressions(
        self, mock_bigquery_client, mock_query_bq, mock_update_or_create
    ):
        """Test that adding two exact flights will update number of clicks and impressions"""
        mock_query_job = MagicMock()
        mock_query_job.result.return_value.to_dataframe.return_value = pd.DataFrame(
            {
                "submission_date": ["2024-09-18", "2024-09-18"],
                "campaign_id": [1, 1],
                "campaign_name": ["Campaign 1", "Campaign 1"],
                "flight_id": [100, 100],
                "flight_name": ["Flight 1", "Flight 1"],
                "provider": ["Provider 1", "Provider 1"],
                "clicks": [10, 15],
                "impressions": [100, 120],
            }
        )

        mock_query_bq.return_value = mock_query_job.result.return_value.to_dataframe()
        mock_bigquery_client.return_value.query.return_value = mock_query_job

        mock_flight_instance = MagicMock(spec=DeliveredFlight)
        mock_flight_instance.clicks_delivered = 10
        mock_flight_instance.impressions_delivered = 100

        # Simulate the side effect of the `update_or_create` calls
        def mock_update_or_create_effect(*args, **kwargs):
            if kwargs["defaults"]["clicks_delivered"] == 10:
                return (mock_flight_instance, True)
            elif kwargs["defaults"]["clicks_delivered"] == 15:
                mock_flight_instance.clicks_delivered = 15
                mock_flight_instance.impressions_delivered = 120
                return (mock_flight_instance, False)

        mock_update_or_create.side_effect = mock_update_or_create_effect

        with self.assertLogs("sync_bigquery_ads_data", level="INFO") as log:
            call_command("sync_bq_data", date="2024-09-18")

        self.assertEqual(mock_update_or_create.call_count, 2)

        mock_update_or_create.assert_any_call(
            submission_date="2024-09-18",
            campaign_id=1,
            flight_id=100,
            provider="Provider 1",
            defaults={
                "campaign_name": "Campaign 1",
                "flight_name": "Flight 1",
                "clicks_delivered": 10,
                "impressions_delivered": 100,
            },
        )

        mock_update_or_create.assert_any_call(
            submission_date="2024-09-18",
            campaign_id=1,
            flight_id=100,
            provider="Provider 1",
            defaults={
                "campaign_name": "Campaign 1",
                "flight_name": "Flight 1",
                "clicks_delivered": 15,
                "impressions_delivered": 120,
            },
        )

        self.assertEqual(mock_flight_instance.clicks_delivered, 15)
        self.assertEqual(mock_flight_instance.impressions_delivered, 120)

        self.assertIn(
            "INFO:sync_bigquery_ads_data:Created new DeliveredFlight", log.output[0]
        )
        self.assertIn(
            "INFO:sync_bigquery_ads_data:Updated DeliveredFlight", log.output[1]
        )

    @patch.dict(os.environ, {"PROJECT_ID": "test-project"})
    @patch(
        "consvc_shepherd.management.commands.sync_bq_data.DeliveredFlight.objects.update_or_create"
    )
    @patch("consvc_shepherd.management.commands.sync_bq_data.BQSyncer.query_bq")
    @patch("consvc_shepherd.management.commands.sync_bq_data.bigquery.Client")
    @patch(
        "consvc_shepherd.management.commands.sync_bq_data.BQSyncer.update_sync_status"
    )
    def test_sync_multiple_rows(
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
                "flight_name": ["Flight 1", "Flight 2"],
                "provider": ["Provider 1", "Provider 2"],
                "clicks": [10, 20],
                "impressions": [100, 200],
            }
        )

        mock_query_bq.return_value = mock_query_job.result.return_value.to_dataframe()
        mock_bigquery_client.return_value.query.return_value = mock_query_job

        mock_update_or_create.return_value = (MagicMock(), True)

        with self.assertLogs("sync_bigquery_ads_data", level="INFO") as log:
            call_command("sync_bq_data", date="2024-09-18")

        mock_query_bq.assert_called_once()

        self.assertEqual(mock_update_or_create.call_count, 2)

        self.assertIn("Created new DeliveredFlight", log.output[0])

        self.assertIn("Created new DeliveredFlight", log.output[1])

        self.assertIn(
            "BigQuery sync process has completed successfully. Updating sync_status",
            log.output[2],
        )

        mock_update_sync_status.assert_called_once_with(
            "success", "BigQuery sync success"
        )

    @patch.dict(os.environ, {"PROJECT_ID": "test-project"})
    @patch("consvc_shepherd.management.commands.sync_bq_data.BQSyncer.query_bq")
    @patch("consvc_shepherd.management.commands.sync_bq_data.bigquery.Client")
    @patch(
        "consvc_shepherd.management.commands.sync_bq_data.DeliveredFlight.objects.update_or_create"
    )
    def test_sync_data_default_arguments(
        self, mock_update_or_create, mock_bigquery_client, mock_query_bq
    ):
        """Test the sync_bq_data command without arguments defaults to today's date"""
        mock_query_job = MagicMock()
        mock_query_job.result.return_value.total_rows = 1
        mock_query_job.result.return_value.to_dataframe.return_value = pd.DataFrame(
            {
                "submission_date": [DEFAULT_DATE],
                "campaign_id": [1],
                "campaign_name": ["Campaign 1"],
                "flight_id": [100],
                "flight_name": ["Flight 1"],
                "provider": ["Provider 1"],
                "clicks": [10],
                "impressions": [100],
            }
        )

        mock_query_bq.return_value = mock_query_job.result.return_value.to_dataframe()
        mock_bigquery_client.return_value.query.return_value = mock_query_job
        mock_update_or_create.return_value = (MagicMock(), True)

        call_command("sync_bq_data")

        mock_query_bq.assert_called_once()

        mock_update_or_create.assert_called_once_with(
            submission_date=DEFAULT_DATE,
            campaign_id=1,
            flight_id=100,
            provider="Provider 1",
            defaults={
                "campaign_name": "Campaign 1",
                "flight_name": "Flight 1",
                "clicks_delivered": 10,
                "impressions_delivered": 100,
            },
        )

    @patch.dict(os.environ, {"PROJECT_ID": "test-project"})
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
            call_command("sync_bq_data", date="2024-09-18")

        self.assertIn("No data returned for date 2024-09-18", str(context.exception))
        mock_update_or_create.assert_not_called()

    @patch.dict(os.environ, {"PROJECT_ID": "invalid_project_id"})
    @patch("consvc_shepherd.management.commands.sync_bq_data.bigquery.Client")
    def test_invalid_project_id(self, mock_bigquery_client):
        """Test the command raises an error for an invalid project ID"""
        mock_bigquery_client.side_effect = Exception("Invalid project ID")

        with self.assertRaises(CommandError) as context:
            call_command("sync_bq_data", date="2024-09-18")

        self.assertIn("Invalid project ID: invalid_project_id", str(context.exception))

    @patch.dict(os.environ, {"PROJECT_ID": "test-project"})
    def test_invalid_date(self):
        """Test that the command raises CommandError for an invalid date format"""
        with self.assertRaises(CommandError) as context:
            call_command("sync_bq_data", date="18-09-2024")

        self.assertIn(
            "Invalid date format. Please use YYYY-MM-DD", str(context.exception)
        )
