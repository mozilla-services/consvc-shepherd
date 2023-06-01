"""Views test module for consvc_shepherd."""
from django.test import TestCase, override_settings

from consvc_shepherd.models import SettingsSnapshot


# override DEBUG to override auth check
@override_settings(DEBUG=True)
class TestTableOverviewCompareSnapshot(TestCase):
    """Test of view when SettingSnapshot updated."""

    def test_view_returns_post_request(self):
        """Verify POST returns 200 response after creating and posting
        settings snapshot.
        """
        SettingsSnapshot.objects.create(
            name="o_snapshot", json_settings={"adm_advertisers": {"advertiser1": {}}}
        )
        SettingsSnapshot.objects.create(
            name="n_snapshot",
            json_settings={"adm_advertisers": {"advertiser2": {}, "advertiser3": {}}},
        )

        data = {"older_snapshot": "o_snapshot", "newer_snapshot": "n_snapshot"}

        response = self.client.post(
            "",
            data,
            **{"settings.OPENIDC_HEADER": "dev@example.com"},
        )
        self.assertEqual(response.status_code, 200)
