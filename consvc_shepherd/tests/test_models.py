"""Tests for consvc_shepherd Models."""

from django.test import TestCase
from django.utils import timezone

from consvc_shepherd.models import (
    AllocationSetting,
    BoostrDeal,
    Campaign,
    CampaignSummary,
    DeliveredFlight,
    Flight,
    Partner,
    PartnerAllocation,
)


class TestAllocationSettingModel(TestCase):
    """Test class for AllocationSettings model."""

    def test_to_dict_produces_correctly(self) -> None:
        """Test for verifying to_dict() method for AllocationSetting"""
        amp_partner: Partner = Partner.objects.create(name="amp")
        moz_partner: Partner = Partner.objects.create(name="moz-sales")
        position1_alloc: AllocationSetting = AllocationSetting.objects.create(
            position=1
        )

        PartnerAllocation.objects.create(
            allocation_position=position1_alloc, partner=amp_partner, percentage=85
        )
        PartnerAllocation.objects.create(
            allocation_position=position1_alloc, partner=moz_partner, percentage=15
        )

        expected_result: dict = {
            "position": 1,
            "allocation": [
                {"partner": "amp", "percentage": 85},
                {"partner": "moz-sales", "percentage": 15},
            ],
        }
        self.assertEqual(position1_alloc.to_dict(), expected_result)
        self.assertEqual(str(position1_alloc), "Allocation Position : 1")


class TestPartnerAllocationModel(TestCase):
    """Test class for PartnerAllocation model."""

    def test_to_dict_produces_correctly(self) -> None:
        """Test for verifying to_dict() method for PartnerAllocation"""
        amp_partner: Partner = Partner.objects.create(name="amp")
        position1_alloc: AllocationSetting = AllocationSetting.objects.create(
            position=1
        )
        allocation1_adm: PartnerAllocation = PartnerAllocation.objects.create(
            allocation_position=position1_alloc, partner=amp_partner, percentage=85
        )
        self.assertEqual(
            allocation1_adm.to_dict(), {"partner": "amp", "percentage": 85}
        )


class CampaignTestCase(TestCase):
    """Test case for Campaign model operations."""

    def setUp(self):
        """Set up test data for Campaign and related models."""
        # Create a BoostrDeal instance to use in Campaign
        self.deal = BoostrDeal.objects.create(
            boostr_id=1,
            name="Test Deal",
            advertiser="Test Advertiser",
            currency="$",
            amount=1000,
            sales_representatives="John Doe, Jane Doe",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
        )

        # Create a Campaign instance
        self.campaign = Campaign.objects.create(
            ad_ops_person="John Doe",
            notes="Test notes",
            net_spend=1000,
            impressions_sold=1000,
            seller="Test Seller",
            deal=self.deal,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
        )

        Flight.objects.create(
            campaign=self.campaign,
            flight_id=12345,
        )

    def test_model_fields(self):
        """Test that Campaign model fields are correctly set."""
        self.assertEqual(self.campaign.ad_ops_person, "John Doe")
        self.assertEqual(self.campaign.notes, "Test notes")
        self.assertEqual(self.campaign.kevel_flight_id, 12345)
        self.assertEqual(self.campaign.net_spend, 1000)
        self.assertEqual(self.campaign.impressions_sold, 1000)
        self.assertEqual(self.campaign.seller, "Test Seller")
        self.assertEqual(self.campaign.deal, self.deal)

    def test_save_method(self):
        """Test the save method calculates net_ecpm correctly."""
        # Test the save method functionality
        campaign = Campaign(
            ad_ops_person="Test Person",
            notes="Test Notes",
            net_spend=2000,
            impressions_sold=500,
            seller="Test Seller",
            deal=self.deal,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
        )
        Flight.objects.create(
            campaign=self.campaign,
            flight_id=11111,
        )

        campaign.save()
        self.assertEqual(campaign.net_ecpm, round((2000 / 500 * 1000), 2))  # 4000

    def test_str_method(self):
        """Verify that the __str__ method returns the correct string representation."""
        expected_str = "Campaign 12345 - John Doe"
        self.assertEqual(str(self.campaign), expected_str)


class CampaignSummaryTestCase(TestCase):
    """Test case for CampaignSummary view operations."""

    def setUp(self):
        """Set up test data for CampaignSummary model."""
        self.campaign_summary = CampaignSummary(
            deal_id=1,
            advertiser="Test Advertiser",
            net_spend=10000,
            impressions_sold=6000,
            clicks_delivered=100,
            impressions_delivered=900,
        )

    def test_campaign_summary_fields(self):
        """Test computed properties of CampaignSummary."""
        self.assertEqual(
            self.campaign_summary.net_ecpm, round(10000 / 6000 * 1000, 2)
        )  # 1666.67
        self.assertEqual(self.campaign_summary.ctr, round(100 / 900 * 100, 2))  # 11.11
        self.assertEqual(
            self.campaign_summary.impressions_remaining, 6000 - 900
        )  # 5100
        self.assertEqual(self.campaign_summary.live, "Yes")


class DeliveredFlightTestCase(TestCase):
    """Test case for DeliveredFlight model operations."""

    def setUp(self):
        """Set up test data for DeliveredFlight model."""
        self.delivered_flight = DeliveredFlight.objects.create(
            submission_date=timezone.now(),
            campaign_id=12345,
            campaign_name="Campaign Name",
            flight_id=54321,
            flight_name="Flight Name",
            provider="kevel",
            clicks_delivered=100,
            impressions_delivered=1000,
        )

    def test_str_method(self):
        """Verify that the __str__ method returns the correct string representation."""
        expected_str = (
            f"{self.delivered_flight.flight_id} : "
            + f"{self.delivered_flight.clicks_delivered} clicks and "
            + f"{self.delivered_flight.impressions_delivered} impressions"
        )
        self.assertEqual(str(self.delivered_flight), expected_str)

    def test_delivered_flight_fields(self):
        """Test that Campaign model fields are correctly set."""
        self.assertEqual(self.delivered_flight.campaign_id, 12345)
        self.assertEqual(self.delivered_flight.campaign_name, "Campaign Name")
        self.assertEqual(self.delivered_flight.flight_id, 54321)
        self.assertEqual(self.delivered_flight.flight_name, "Flight Name")
        self.assertEqual(self.delivered_flight.provider, "kevel")
        self.assertEqual(self.delivered_flight.clicks_delivered, 100)
        self.assertEqual(self.delivered_flight.impressions_delivered, 1000)


class FlightTestCase(TestCase):
    """Test case for Flight model operations."""

    def setUp(self):
        """Set up test data for Flight model."""
        self.deal = BoostrDeal.objects.create(
            boostr_id=1,
            name="Test Deal",
            advertiser="Test Advertiser",
            currency="$",
            amount=1000,
            sales_representatives="John Doe, Jane Doe",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
        )

        self.campaign = Campaign.objects.create(
            ad_ops_person="John Doe",
            notes="Test notes",
            net_spend=1000,
            impressions_sold=1000,
            seller="Test Seller",
            deal=self.deal,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
        )

        self.flight = Flight.objects.create(
            campaign=self.campaign,
            flight_id=54321,
        )

    def test_model_fields(self):
        """Test that Flight model fields are correctly set."""
        self.assertEqual(self.flight.campaign, self.campaign)
        self.assertEqual(self.flight.flight_id, 54321)

    def test_str_method(self):
        """Verify that the __str__ method returns the correct string representation."""
        expected_str = "Flight 54321"
        self.assertEqual(str(self.flight), expected_str)
