"""Forms test module for consvc_shepherd."""
from django.test import TestCase

from consvc_shepherd.forms import SnapshotCompareForm
from consvc_shepherd.models import SettingsSnapshot


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
