"""Tests for consvc_shepherd Models."""

from django.test import TestCase

from consvc_shepherd.models import (
    AllocationSetting,
    DeliveredCampaign,
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


class TestDeliveredCampaignModel(TestCase):
    """Test class for DeliveredCampaign model."""

    def setUp(self):
        """Set up a DeliveredCampaign instance for testing."""
        self.campaign = DeliveredCampaign.objects.create(
            submission_date="2023-09-13",
            flight_id=123456789,
            campaign_id=987654321,
            surface="desktop",
            country="US",
            product="Tiles",
            provider="kevel",
            clicks=100,
            impressions=1000,
        )

    def test_campaign_creation(self):
        """Test if the campaign is created correctly."""
        self.assertEqual(self.campaign.flight_id, 123456789)
        self.assertEqual(self.campaign.clicks, 100)
        self.assertEqual(self.campaign.impressions, 1000)

    def test_campaign_str(self):
        """Test the __str__ method returns the flight IDs along with number of clicks and impressions"""
        self.assertEqual(
            str(self.campaign), "123456789 : 100 clicks and 1000 impressions"
        )
