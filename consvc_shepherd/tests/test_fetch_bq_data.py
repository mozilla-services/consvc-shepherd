"""Unit tests for the fetch_bq_data command"""

from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pandas as pd
from django.core.management import call_command
from django.core.management.base import CommandError


class TestBQFetcherData(TestCase):
    """Unit tests for functions that fetch from BigQuery and store in our DB"""

    @patch(
        "consvc_shepherd.management.commands.fetch_bq_data.DeliveredFlight.objects.update_or_create"
    )
    @patch("consvc_shepherd.management.commands.fetch_bq_data.BQFetcher.query_bq")
    @patch("consvc_shepherd.management.commands.fetch_bq_data.bigquery.Client")
    def test_fetch_data_successful(
        self, mock_bigquery_client, mock_query_bq, mock_update_or_create
    ):
        """Test that fetch_data attempts to insert data into DB when successful"""
        # Mock obj to simulate BigQuery client and its query method
        mock_query_job = MagicMock()
        mock_query_job.result.return_value.total_rows = 1
        mock_query_job.result.return_value.to_dataframe.return_value = pd.DataFrame(
            {
                "submission_date": ["2024-09-18"],
                "campaign_id": [1],
                "campaign_name": ["Campaign 1"],
                "flight_id": [100],
                "flight_name": ["Flight 1"],
                "country": ["US"],
                "provider": ["Provider 1"],
                "clicks": [10],
                "impressions": [100],
            }
        )

        mock_query_bq.return_value = mock_query_job.result.return_value.to_dataframe()

        mock_bigquery_client.return_value.query.return_value = mock_query_job

        # Mock the update_or_create behavior
        mock_update_or_create.return_value = (MagicMock(), True)  # Simulating creation

        # Call the management command
        call_command("fetch_bq_data", project_id="test-project", date="2024-09-18")

        # Assert that the BigQuery query method was called
        mock_query_bq.assert_called_once()

        # Assert that update_or_create was called with the correct parameters
        mock_update_or_create.assert_called_once_with(
            submission_date="2024-09-18",
            campaign_id=1,
            campaign_name="Campaign 1",
            flight_id=100,
            flight_name="Flight 1",
            country="US",
            provider="Provider 1",
            defaults={
                "clicks_delivered": 10,
                "impressions_delivered": 100,
            },
        )

    @patch("consvc_shepherd.management.commands.fetch_bq_data.BQFetcher.fetch_data")
    @patch("consvc_shepherd.management.commands.fetch_bq_data.bigquery.Client")
    def test_fetch_data_failure(self, mock_bigquery_client, mock_fetch_data):
        """Test the behavior of the fetch_bq_data command when the fetch_data method fails"""
        # Simulate a failure in the fetch_data method
        mock_fetch_data.side_effect = Exception("Failed to fetch data from BigQuery")

        # Create a mock for the BigQuery client
        mock_bigquery_client.return_value = MagicMock()

        with self.assertRaises(CommandError) as context:
            call_command("fetch_bq_data", project_id="test-project", date="2024-09-18")

        # Verify that the appropriate error message was raised
        self.assertIn(
            "An error occurred: Failed to fetch data from BigQuery",
            str(context.exception),
        )

    @patch(
        "consvc_shepherd.management.commands.fetch_bq_data.DeliveredFlight.objects.update_or_create"
    )
    @patch("consvc_shepherd.management.commands.fetch_bq_data.bigquery.Client")
    def test_no_data_returned_for_date(
        self, mock_bigquery_client, mock_update_or_create
    ):
        """Test the command returns an error if BigQuery doesn't return data for a given date"""
        mock_query_job = MagicMock()
        mock_query_job.result.return_value.total_rows = (
            0  # Simulate no rows returned from BigQuery
        )
        mock_query_job.result.return_value.to_dataframe.return_value = (
            pd.DataFrame()
        )  # Empty DataFrame

        # Make the bigquery client return this mocked job when queried
        mock_bigquery_client.return_value.query.return_value = mock_query_job

        with self.assertLogs("sync_bigquery_ads_data", level="ERROR") as log:
            call_command("fetch_bq_data", project_id="test-project", date="2024-09-18")

        # Check that an error log was produced
        self.assertIn("No data returned for the date 2024-09-18", log.output[0])
        mock_update_or_create.assert_not_called()

    @patch("consvc_shepherd.management.commands.fetch_bq_data.bigquery.Client")
    def test_invalid_project_id(self, mock_bigquery_client):
        """Test the command raises an error for an invalid project ID"""
        # Simulate an exception being raised when trying to create a BigQuery client
        mock_bigquery_client.side_effect = Exception("Invalid project ID")

        with self.assertRaises(CommandError) as context:
            call_command(
                "fetch_bq_data", project_id="invalid_project_id", date="2024-09-18"
            )

        # Verify that the appropriate error message was output
        self.assertIn("Invalid project ID: invalid_project_id", str(context.exception))

    @patch(
        "consvc_shepherd.management.commands.fetch_bq_data.DeliveredFlight.objects.update_or_create"
    )
    @patch("consvc_shepherd.management.commands.fetch_bq_data.BQFetcher.query_bq")
    @patch("consvc_shepherd.management.commands.fetch_bq_data.bigquery.Client")
    def test_fetch_data_multiple_rows(
        self, mock_bigquery_client, mock_query_bq, mock_update_or_create
    ):
        """Test that fetch_data processes multiple rows returned from BigQuery"""
        # Mock obj to simulate BigQuery client and its query method
        mock_query_job = MagicMock()
        mock_query_job.result.return_value.total_rows = 2
        mock_query_job.result.return_value.to_dataframe.return_value = pd.DataFrame(
            {
                "submission_date": ["2024-09-18", "2024-09-18"],
                "campaign_id": [1, 2],
                "campaign_name": ["Campaign 1", "Campaign 2"],
                "flight_id": [100, 101],
                "flight_name": ["Flight 1", "Flight 2"],
                "country": ["US", "BR"],
                "provider": ["Provider 1", "Provider 2"],
                "clicks": [10, 20],
                "impressions": [100, 200],
            }
        )

        mock_query_bq.return_value = mock_query_job.result.return_value.to_dataframe()
        mock_bigquery_client.return_value.query.return_value = mock_query_job

        # Mock the update_or_create behavior
        mock_update_or_create.return_value = (MagicMock(), True)  # Simulating creation

        # Call the management command
        call_command("fetch_bq_data", project_id="test-project", date="2024-09-18")

        # Assert that the BigQuery query method was called
        mock_query_bq.assert_called_once()

        # Assert that update_or_create was called twice for both rows
        self.assertEqual(mock_update_or_create.call_count, 2)

    @patch("consvc_shepherd.management.commands.fetch_bq_data.BQFetcher.query_bq")
    @patch("consvc_shepherd.management.commands.fetch_bq_data.bigquery.Client")
    @patch(
        "consvc_shepherd.management.commands.fetch_bq_data.DeliveredFlight.objects.update_or_create"
    )
    def test_fetch_data_default_date(
        self, mock_update_or_create, mock_bigquery_client, mock_query_bq
    ):
        """Test the fetch_bq_data command without a date argument defaults to today's date."""
        # Mocking the expected output from BigQuery
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
                "flight_name": ["Flight 1"],
                "country": ["US"],
                "provider": ["Provider 1"],
                "clicks": [10],
                "impressions": [100],
            }
        )

        mock_query_bq.return_value = mock_query_job.result.return_value.to_dataframe()
        mock_bigquery_client.return_value.query.return_value = mock_query_job

        # Call the management command without the date argument
        call_command("fetch_bq_data", project_id="test-project")

        # Assert that the BigQuery query method was called
        mock_query_bq.assert_called_once()

        # Assert that the query was executed with today's date
        # Check if update_or_create was called with the correct parameters
        mock_update_or_create.assert_called_once_with(
            submission_date=datetime.today().strftime("%Y-%m-%d"),
            campaign_id=1,
            campaign_name="Campaign 1",
            flight_id=100,
            flight_name="Flight 1",
            country="US",
            provider="Provider 1",
            defaults={
                "clicks_delivered": 10,
                "impressions_delivered": 100,
            },
        )
