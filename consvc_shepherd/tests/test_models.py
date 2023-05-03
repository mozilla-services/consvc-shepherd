"""Tests for consvc_shepherd Models."""
from django.test import TestCase

from consvc_shepherd.models import AllocationSetting, Partner, PartnerAllocation


class TestAllocationSettingModel(TestCase):
    """Test class for AllocationSettings model."""

    def test_to_dict_produces_correctly(self) -> None:
        """Test for verifying to_dict() method for AllocationSetting"""
        adm_partner: Partner = Partner.objects.create(name="adm")
        kevel_partner: Partner = Partner.objects.create(name="kevel")
        position1_alloc: AllocationSetting = AllocationSetting.objects.create(
            position=1
        )
        allocation1_adm: PartnerAllocation = (  # noqa: F841
            PartnerAllocation.objects.create(
                allocationPosition=position1_alloc, partner=adm_partner, percentage=85
            )
        )
        allocation1_kevel: PartnerAllocation = (  # noqa: F841
            PartnerAllocation.objects.create(
                allocationPosition=position1_alloc, partner=kevel_partner, percentage=15
            )
        )
        expected_result: dict = {
            "position": 1,
            "allocation": {"adm": 85, "kevel": 15},
        }
        self.assertEqual(position1_alloc.to_dict(), expected_result)


class TestPartnerAllocationModel(TestCase):
    """Test class for PartnerAllocation model."""

    def test_to_dict_produces_correctly(self) -> None:
        """Test for verifying to_dict() method for PartnerAllocation"""
        adm_partner: Partner = Partner.objects.create(name="adm")
        kevel_partner: Partner = Partner.objects.create(name="kevel")
        position1_alloc: AllocationSetting = AllocationSetting.objects.create(
            position=1
        )
        allocation1_adm: PartnerAllocation = PartnerAllocation.objects.create(
            allocationPosition=position1_alloc, partner=adm_partner, percentage=85
        )
        allocation1_kevel: PartnerAllocation = PartnerAllocation.objects.create(
            allocationPosition=position1_alloc, partner=kevel_partner, percentage=15
        )
        self.assertEqual(
            allocation1_adm.to_dict(), {"position": 1, "allocation": {"adm": 85}}
        )
        self.assertEqual(
            allocation1_kevel.to_dict(), {"position": 1, "allocation": {"kevel": 15}}
        )
