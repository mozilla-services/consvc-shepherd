"""Tests for consvc_shepherd Models."""

from django.test import TestCase
from django.utils import timezone

from consvc_shepherd.models import (
    AllocationSetting,
    BoostrDeal,
    CampaignOverview,
    CampaignOverviewSummary,
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


class CampaignOverviewTestCase(TestCase):
    """Test case for CampaignOverview model operations."""

    def setUp(self):
        """Set up test data for CampaignOverview and related models."""
        # Create a BoostrDeal instance to use in CampaignOverview
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

        # Create a CampaignOverview instance
        self.campaign = CampaignOverview.objects.create(
            ad_ops_person="John Doe",
            notes="Test notes",
            kevel_flight_id=12345,
            net_spend=1000,
            impressions_sold=1000,
            seller="Test Seller",
            deal=self.deal,
        )

    def test_model_fields(self):
        """Test that CampaignOverview model fields are correctly set."""
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
        campaign = CampaignOverview(
            ad_ops_person="Test Person",
            notes="Test Notes",
            kevel_flight_id=11111,
            net_spend=2000,
            impressions_sold=500,
            seller="Test Seller",
            deal=self.deal,
        )
        campaign.save()
        self.assertEqual(campaign.net_ecpm, (2000 / 500) * 1000)  # 4000

    def test_str_method(self):
        """Verify that the __str__ method returns the correct string representation."""
        expected_str = "John Doe - 12345"
        self.assertEqual(str(self.campaign), expected_str)


class CampaignOverviewSummaryTestCase(TestCase):
    """Test case for the CampaignOverviewSummary proxy model."""

    def test_proxy_model(self):
        """Verify the proxy model's verbose names and proxy status."""
        # Check that the proxy model uses the correct verbose names
        self.assertEqual(CampaignOverviewSummary._meta.verbose_name, "Campaign Summary")
        self.assertEqual(
            CampaignOverviewSummary._meta.verbose_name_plural, "Campaign Summaries"
        )
        self.assertTrue(CampaignOverviewSummary._meta.proxy)
