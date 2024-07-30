"""Views test module for consvc_shepherd."""

from unittest import mock

from django.test import TestCase, override_settings

from consvc_shepherd.models import (
    AllocationSetting,
    AllocationSettingsSnapshot,
    PartnerAllocation,
    SettingsSnapshot,
)
from consvc_shepherd.preview import Ads, Spoc, Tile
from contile.models import Partner


# override DEBUG to override auth check
@override_settings(DEBUG=True)
class TestTableOverviewCompareSnapshot(TestCase):
    """Test of view when SettingSnapshot updated."""

    def test_view_returns_post_request(self):
        """Verify POST returns 200 response after comparing
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


@override_settings(DEBUG=True)
class TestAllocationCreateView(TestCase):
    """Test of Allocation View."""

    def test_create_view_returns_post_request(self):
        """Verify POST returns 302 response after creating
        Allocation Setting.
        """
        partner1 = Partner.objects.create(name="partner1")
        partner2 = Partner.objects.create(name="partner2")
        data = {
            "position": "1",
            "partner_allocations-TOTAL_FORMS": "2",
            "partner_allocations-INITIAL_FORMS": "0",
            "partner_allocations-MIN_NUM_FORMS": "0",
            "partner_allocations-MAX_NUM_FORMS": "1000",
            "partner_allocations-0-id": "",
            "partner_allocations-0-allocation_position": "",
            "partner_allocations-0-partner": f"{partner1.id}",
            "partner_allocations-0-percentage": "50",
            "partner_allocations-1-id": "",
            "partner_allocations-1-allocation_position": "",
            "partner_allocations-1-partner": f"{partner2.id}",
            "partner_allocations-1-percentage": "50",
            "partner_allocations-__prefix__-id": "",
            "partner_allocations-__prefix__-allocation_position": "",
            "partner_allocations-__prefix__-partner": "",
            "partner_allocations-__prefix__-percentage": "",
        }

        response = self.client.post(
            "/allocation/create/",
            data,
            **{"settings.OPENIDC_HEADER": "dev@example.com"},
        )
        self.assertEqual(response.status_code, 302)

    def test_update_view_returns_post_request(self):
        """Verify POST returns 302 response after updating
        Allocation Setting.
        """
        partner1 = Partner.objects.create(name="partner1")
        partner2 = Partner.objects.create(name="partner2")

        alloc_setting = AllocationSetting.objects.create(position=2)
        PartnerAllocation.objects.create(
            allocation_position=alloc_setting, partner=partner1, percentage=100
        )

        data = {
            "position": "2",
            "partner_allocations-TOTAL_FORMS": "2",
            "partner_allocations-INITIAL_FORMS": "0",
            "partner_allocations-MIN_NUM_FORMS": "0",
            "partner_allocations-MAX_NUM_FORMS": "1000",
            "partner_allocations-0-id": "",
            "partner_allocations-0-allocation_position": "",
            "partner_allocations-0-partner": f"{partner1.id}",
            "partner_allocations-0-percentage": "50",
            "partner_allocations-1-id": "",
            "partner_allocations-1-allocation_position": "",
            "partner_allocations-1-partner": f"{partner2.id}",
            "partner_allocations-1-percentage": "50",
            "partner_allocations-__prefix__-id": "",
            "partner_allocations-__prefix__-allocation_position": "",
            "partner_allocations-__prefix__-partner": "",
            "partner_allocations-__prefix__-percentage": "",
        }

        response = self.client.post(
            f"/allocation/{alloc_setting.id}/",
            data,
            **{"settings.OPENIDC_HEADER": "dev@example.com"},
        )
        self.assertEqual(response.status_code, 302)


# override DEBUG to override auth check
@override_settings(DEBUG=True)
class TestAllocationSettingsListView(TestCase):
    """Test of view when SettingSnapshot updated."""

    def test_view_returns_post_request(self):
        """Verify POST returns 200 response after creating and posting
        settings snapshot.
        """
        data = {"name": "snapshot1"}
        partner = Partner.objects.create(name="amp")
        alloc_setting_1 = AllocationSetting.objects.create(position=1)
        alloc_setting_2 = AllocationSetting.objects.create(position=2)
        PartnerAllocation.objects.create(
            allocation_position=alloc_setting_1, partner=partner, percentage=100
        )
        PartnerAllocation.objects.create(
            allocation_position=alloc_setting_2, partner=partner, percentage=100
        )
        self.assertEqual(AllocationSettingsSnapshot.objects.count(), 0)
        response = self.client.post(
            "/allocation/",
            data,
            **{"settings.OPENIDC_HEADER": "dev@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AllocationSettingsSnapshot.objects.count(), 1)


@override_settings(DEBUG=True)
class TestPreviewView(TestCase):
    """Test of PreviewView."""

    def createMockAds(self):
        """Create some mock ads data to assert against in the preview view"""
        tile = Tile(
            image_url="https://picsum.photos/48",
            name="ACME",
            sponsored="Sponsored",
            url="example.com",
        )
        direct_sold_tile = Tile(
            image_url="https://picsum.photos/48",
            name="Zombocom",
            sponsored="Sponsored",
            url="example.com",
        )
        spoc = Spoc(
            image_src="https://picsum.photos/296/148",
            title="Play Anvil of the Ages Now for Free",
            domain="play.anviloftheages.com",
            excerpt="If you like to play games, then you should play this game.",
            sponsored_by="Anvil of the Ages",
            sponsor="Anvil of the Ages",
            url="example.com",
        )
        return Ads(
            tiles=[tile, direct_sold_tile],
            spocs=[spoc],
        )

    def test_preview_view(self):
        """Test that the preview view shows data returned from get_ads request"""
        with mock.patch(
            "consvc_shepherd.preview.get_ads", return_value=self.createMockAds()
        ):
            response = self.client.get("/preview")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["ads"].tiles), 2)
            self.assertContains(response, "ACME")
            self.assertContains(response, "Zombocom")
            self.assertEqual(len(response.context["ads"].spocs), 1)
            self.assertContains(response, "Anvil of the Ages")
