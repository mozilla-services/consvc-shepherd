"""Tests for consvc_shepherd Models."""
from django.test import TestCase

from consvc_shepherd.models import AllocationSetting, Partner, PartnerAllocation


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
            allocation_position=position1_alloc, partner=amp_partner, percentage=100
        )
        self.assertEqual(
            allocation1_adm.to_dict(), {"partner": "amp", "percentage": 100}
        )
