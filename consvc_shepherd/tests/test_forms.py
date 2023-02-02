from django.test import TestCase

from consvc_shepherd.forms import SnapshotCompareForm
from consvc_shepherd.models import SettingsSnapshot


class TestSnapshotCompareForm(TestCase):
    def test_required_fields_for_form(self):
        data = {
            "newer_snapshot": "Snapshot 1",
        }
        form = SnapshotCompareForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {"older_snapshot": ["This field is required."]})

    def test_compare_returns_differences(self):
        SettingsSnapshot.objects.create(
            name="o_snapshot", json_settings={"adm_advertisers": {"advertiser1": {}}}
        )
        SettingsSnapshot.objects.create(
            name="n_snapshot",
            json_settings={"adm_advertisers": {"advertiser2": {}, "advertiser3": {}}},
        )
        data = {"older_snapshot": "o_snapshot", "newer_snapshot": "n_snapshot"}
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
