"""Forms test module for consvc_shepherd."""

from django.test import TestCase

from consvc_shepherd.forms import (
    AllocationFormset,
    AllocationSettingsSnapshotForm,
    SnapshotCompareForm,
)
from consvc_shepherd.models import (
    AllocationSetting,
    PartnerAllocation,
    SettingsSnapshot,
)
from contile.models import Partner


class TestSnapshotCompareForm(TestCase):
    """Test Snapshot Compare Form."""

    def test_required_fields_for_form(self):
        """Test that validation error occurs when missing a required field."""
        data = {
            "newer_snapshot": "Snapshot 1",
        }
        form = SnapshotCompareForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["older_snapshot"], ["This field is required."])

    def test_compare_returns_differences(self):
        """Test that comparison between old and new snapshots returns differences in
        data representation.
        """
        snapshot1 = SettingsSnapshot.objects.create(
            name="o_snapshot", json_settings={"adm_advertisers": {"advertiser1": {}}}
        )
        snapshot2 = SettingsSnapshot.objects.create(
            name="n_snapshot",
            json_settings={"adm_advertisers": {"advertiser2": {}, "advertiser3": {}}},
        )
        data = {"older_snapshot": snapshot1.id, "newer_snapshot": snapshot2.id}
        form = SnapshotCompareForm(data=data)
        self.assertTrue(form.is_valid())
        differences = form.compare()
        expected_differences = {
            "differences": [
                {
                    "diff_type": "Added Advertisers",
                    "diff_value": ["advertiser2", "advertiser3"],
                },
                {"diff_type": "Removed Advertisers", "diff_value": ["advertiser1"]},
            ],
            "title": "Comparing o_snapshot with n_snapshot",
        }
        self.assertEqual(differences, expected_differences)


class TestAllocationFormSet(TestCase):
    """Test Allocation FormSet."""

    def setUp(self):
        """Set up data for tests."""
        self.partner1 = Partner.objects.create(name="partner1")
        self.partner2 = Partner.objects.create(name="partner2")
        self.data = {
            "position": "1",
            "partner_allocations-TOTAL_FORMS": "2",
            "partner_allocations-INITIAL_FORMS": "0",
            "partner_allocations-MIN_NUM_FORMS": "0",
            "partner_allocations-MAX_NUM_FORMS": "1000",
            "partner_allocations-0-id": "",
            "partner_allocations-0-allocation_position": "",
            "partner_allocations-0-partner": f"{self.partner1.id}",
            "partner_allocations-0-percentage": "50",
            "partner_allocations-1-id": "",
            "partner_allocations-1-allocation_position": "",
            "partner_allocations-1-partner": f"{self.partner2.id}",
            "partner_allocations-1-percentage": "50",
            "partner_allocations-__prefix__-id": "",
            "partner_allocations-__prefix__-allocation_position": "",
            "partner_allocations-__prefix__-partner": "",
            "partner_allocations-__prefix__-percentage": "",
        }

    def test_returns_no_errors_for_valid_form(self):
        """Test to ensure forms.ValidationError is raise when form percents does
        not add up to 100.
        """
        form = AllocationFormset(data=self.data)
        self.assertTrue(form.is_valid())

    def test_returns_errors_when_percentage_does_not_sum_to_100(self):
        """Test to ensure forms.ValidationError is raise when form percents does
        not add up to 100.
        """
        self.data["partner_allocations-1-percentage"] = "55"
        form = AllocationFormset(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_form_errors(), ["Total Percentage has to add up to 100."]
        )

    def test_returns_errors_when_partners_are_not_unique(self):
        """Test to ensure forms.ValidationError is raise when partners
        are not unique.
        """
        self.data["partner_allocations-1-partner"] = f"{self.partner1.id}"
        form = AllocationFormset(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_form_errors(), ["A Partner is listed multiple times."]
        )

    def test_returns_valid_with_one_blank_form_set(self):
        """Test to ensure blank form is ignored when validating form data"""
        extra_blank_form = {
            "partner_allocations-2-id": "",
            "partner_allocations-2-allocation_position": "",
            "partner_allocations-2-partner": "",
            "partner_allocations-2-percentage": "",
        }
        self.data.update(extra_blank_form)
        form = AllocationFormset(data=self.data)
        self.assertTrue(form.is_valid())


class TestAllocationSettingsSnapshotForm(TestCase):
    """Test Allocation Snapshot Form."""

    def test_form_raises_error_with_invalid_json(self):
        """Test that validation error occurs when missing a required field."""
        Partner.objects.create(name="amp")
        AllocationSetting.objects.create(position=1)
        data = {
            "name": "Snapshot 1",
        }
        form = AllocationSettingsSnapshotForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_returns_true_when_valid(self):
        """Test that validation error occurs when missing a required field."""
        partner = Partner.objects.create(name="amp")
        alloc_setting_1 = AllocationSetting.objects.create(position=1)
        alloc_setting_2 = AllocationSetting.objects.create(position=2)
        PartnerAllocation.objects.create(
            allocation_position=alloc_setting_1, partner=partner, percentage=100
        )
        PartnerAllocation.objects.create(
            allocation_position=alloc_setting_2, partner=partner, percentage=100
        )
        data = {
            "name": "Snapshot 1",
        }
        form = AllocationSettingsSnapshotForm(data=data)
        self.assertTrue(form.is_valid())
