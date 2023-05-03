import json
from typing import Any

import mock
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.utils import timezone
from jsonschema import validate

from consvc_shepherd.admin import ModelAdmin, publish_allocation, publish_snapshot
from consvc_shepherd.models import (
    AllocationSetting,
    Partner,
    PartnerAllocation,
    SettingsSnapshot,
)
from consvc_shepherd.tests.factories import UserFactory
from contile.models import Advertiser, AdvertiserUrl


class SettingsSnapshotAdminTest(TestCase):
    """Test class for SettingsSnapshot."""

    def setUp(self):
        request_factory = RequestFactory()
        self.request = request_factory.get("/admin")
        self.request.user = UserFactory()

        with open("./schema/adm_filter.schema.json", "r") as f:
            self.settings_schema = json.load(f)

        site = AdminSite()
        self.admin = ModelAdmin(SettingsSnapshot, site)

        self.partner = Partner.objects.create(name="Partner1")
        advertiser = Advertiser.objects.create(partner=self.partner, name="Advertiser1")
        AdvertiserUrl.objects.create(
            advertiser=advertiser,
            geo="CA",
            domain="example.com",
            path="/",
            matching=True,
        )
        self.partner = Partner.objects.get(name="Partner1")
        self.mock_storage_open = mock.patch(
            "django.core.files.storage.default_storage." "open"
        )
        self.mock_storage_open.start()
        self.addCleanup(self.mock_storage_open.stop)

    def test_get_read_only_fields_when_obj_exists(self):
        obj = SettingsSnapshot.objects.create(
            name="Snapshot", settings_type=self.partner
        )
        fields = self.admin.get_readonly_fields(self.request, obj)
        self.assertEqual(
            fields,
            [
                "name",
                "settings_type",
                "json_settings",
                "created_by",
                "launched_by",
                "launched_date",
            ],
        )

    def test_get_read_only_fields_when_obj_does_not_exists(self):
        fields = self.admin.get_readonly_fields(self.request, None)
        self.assertEqual(
            fields, ["json_settings", "created_by", "launched_by", "launched_date"]
        )

    def test_save_model_generates_json(self):
        self.assertEqual(SettingsSnapshot.objects.all().count(), 0)

        expected_json = self.partner.to_dict()
        self.admin.save_model(
            self.request,
            SettingsSnapshot(name="dev", settings_type=self.partner),
            None,
            {},
        )

        self.assertEqual(SettingsSnapshot.objects.all().count(), 1)
        snapshot = SettingsSnapshot.objects.all().first()
        validate(snapshot.json_settings, schema=self.settings_schema)
        self.assertEqual(snapshot.json_settings, expected_json)

    def test_publish_snapshot(self):
        request = mock.Mock()
        request.user = UserFactory()

        SettingsSnapshot.objects.create(
            name="Settings Snapshot",
            settings_type=self.partner,
            json_settings=self.partner.to_dict(),
            created_by=request.user,
        )
        publish_snapshot(None, request, SettingsSnapshot.objects.all())
        snapshot = SettingsSnapshot.objects.get(name="Settings Snapshot")
        self.assertIsNotNone(snapshot.launched_date)

        self.assertEqual(snapshot.launched_by, request.user)

    def test_publish_snapshot_does_not_update_with_multiple_snapshots(self):
        request = mock.Mock()
        request.user = UserFactory()
        SettingsSnapshot.objects.create(
            name="Settings Snapshot",
            settings_type=self.partner,
            created_by=request.user,
        )
        SettingsSnapshot.objects.create(
            name="Settings Snapshot",
            settings_type=self.partner,
            created_by=request.user,
        )
        publish_snapshot(None, request, SettingsSnapshot.objects.all())
        snapshots = SettingsSnapshot.objects.filter(
            launched_date=None, launched_by=None
        )
        self.assertEqual(len(snapshots), 2)

    def test_publish_snapshot_does_not_launch_already_launch_snapshot(self):
        request = mock.Mock()
        request.user = UserFactory()
        timestamp = timezone.datetime(2022, 1, 11, 1, 15, 12)
        SettingsSnapshot.objects.create(
            name="Settings Snapshot",
            settings_type=self.partner,
            created_by=request.user,
            launched_date=timestamp,
            launched_by=request.user,
        )
        publish_snapshot(None, request, SettingsSnapshot.objects.all())
        snapshots = SettingsSnapshot.objects.filter(
            launched_date=timezone.now(),
            launched_by=request.user,
        )
        self.assertEqual(len(snapshots), 0)

    def test_snapshot_cannot_be_deleted_when_launched(self):
        request = mock.Mock()
        request.user = UserFactory()
        snapshot = SettingsSnapshot.objects.create(
            name="Settings Snapshot",
            settings_type=self.partner,
            created_by=request.user,
            launched_date=timezone.now(),
            launched_by=request.user,
        )
        self.assertFalse(self.admin.has_delete_permission(request, snapshot))

    def test_snapshot_can_be_deleted_when_unlaunched(self):
        request = mock.Mock()
        request.user = UserFactory()
        snapshot = SettingsSnapshot.objects.create(
            name="Settings Snapshot",
            settings_type=self.partner,
            created_by=request.user,
        )
        self.assertTrue(self.admin.has_delete_permission(request, snapshot))


class AllocationSettingAdminTest(TestCase):
    """Test class for AllocationSetting."""

    def setUp(self):
        request_factory = RequestFactory()
        self.request = request_factory.get("/admin/consvc_shepherd/allocationsetting/")
        self.request.user = UserFactory()

        with open("./schema/allocation.schema.json", "r") as f:
            self.allocation_schema = json.load(f)

        site = AdminSite()
        self.admin = ModelAdmin(AllocationSetting, site)

        allocations: dict[str, Any] = {}
        allocations.update({"name": "SOV-20230101140000", "allocations": []})

        adm_partner: Partner = Partner.objects.create(name="adm")
        kevel_partner: Partner = Partner.objects.create(name="kevel")
        position1_alloc: AllocationSetting = AllocationSetting.objects.create(
            position=1
        )
        PartnerAllocation.objects.create(
            allocationPosition=position1_alloc, partner=adm_partner, percentage=85
        )
        PartnerAllocation.objects.create(
            allocationPosition=position1_alloc, partner=kevel_partner, percentage=15
        )
        self.mock_storage_open = mock.patch(
            "django.core.files.storage.default_storage." "open"
        )
        self.mock_storage_open.start()
        self.addCleanup(self.mock_storage_open.stop)

    def test_publish_allocation(self):
        request = mock.Mock()
        expected: dict = {"position": 1, "allocation": {"adm": 85, "kevel": 15}}

        publish_allocation(None, request, AllocationSetting.objects.all())
        allocation_setting: dict = AllocationSetting.objects.get(position=1).to_dict()
        self.assertEqual(allocation_setting, expected)
