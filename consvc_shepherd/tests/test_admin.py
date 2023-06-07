"""Admin test module for consvc_shepherd."""
import json
from typing import Any

import mock  # type: ignore [import]
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone
from jsonschema import validate
from markus.testing import MetricsMock

from consvc_shepherd.admin import ModelAdmin, publish_allocation, publish_snapshot, AllocationSettingAdmin
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

    def setUp(self) -> None:
        """Set up objects and variables for testing SettingsSnapshot."""
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
        mock_storage_open = mock.patch(
            "django.core.files.storage.default_storage." "open"
        )
        self.mock_storage_open = mock_storage_open.start()
        self.addCleanup(self.mock_storage_open.stop)

    def test_get_read_only_fields_when_obj_exists(self) -> None:
        """Test that expected read only fields are returned when object created."""
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

    def test_get_read_only_fields_when_obj_does_not_exists(self) -> None:
        """Test that read only fields return when object not created."""
        fields = self.admin.get_readonly_fields(self.request, None)
        self.assertEqual(
            fields, ["json_settings", "created_by", "launched_by", "launched_date"]
        )

    def test_save_model_generates_json(self) -> None:
        """Test that snapshot value matches expected json object."""
        self.assertEqual(SettingsSnapshot.objects.all().count(), 0)

        expected_json: dict = self.partner.to_dict()
        self.admin.save_model(
            self.request,
            SettingsSnapshot(name="dev", settings_type=self.partner),
            None,
            {},
        )

        self.assertEqual(SettingsSnapshot.objects.all().count(), 1)
        snapshot = SettingsSnapshot.objects.all().first()
        if snapshot:
            validate(snapshot.json_settings, schema=self.settings_schema)
            self.assertEqual(snapshot.json_settings, expected_json)

    def test_publish_snapshot(self) -> None:
        """Test that publishing snapshot returns expected metadata."""
        request = mock.Mock()
        request.user = UserFactory()

        SettingsSnapshot.objects.create(
            name="Settings Snapshot",
            settings_type=self.partner,
            json_settings=self.partner.to_dict(),
            created_by=request.user,
        )

        publish_snapshot(None, request, SettingsSnapshot.objects.all())
        snapshot: SettingsSnapshot = SettingsSnapshot.objects.get(
            name="Settings Snapshot"
        )
        self.assertIsNotNone(snapshot.launched_date)
        self.assertEqual(snapshot.launched_by, request.user)

    def test_publish_snapshot_does_not_update_with_multiple_snapshots(self) -> None:
        """Test that single publish action does not update with multiple snapshots."""
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

    def test_publish_snapshot_does_not_launch_already_launch_snapshot(self) -> None:
        """Test that publish snapshot action does not launch pre-existing snapshot."""
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

    def test_snapshot_cannot_be_deleted_when_launched(self) -> None:
        """Test that snapshot cannot be deleted once launched."""
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

    def test_snapshot_can_be_deleted_when_unlaunched(self) -> None:
        """Test that snapshot can be deleted when unlaunched."""
        request = mock.Mock()
        request.user = UserFactory()
        snapshot = SettingsSnapshot.objects.create(
            name="Settings Snapshot",
            settings_type=self.partner,
            created_by=request.user,
        )
        self.assertTrue(self.admin.has_delete_permission(request, snapshot))

    @override_settings(STATSD_ENABLED=True)
    def test_delete_settings_snapshot(self) -> None:
        """Test that delete_queryset removes settings snapshot."""
        request = mock.Mock()
        request.user = UserFactory()

        snapshot = SettingsSnapshot.objects.create(
            name="Settings Snapshot",
            settings_type=self.partner,
            json_settings=self.partner.to_dict(),
            created_by=request.user,
        )
        self.assertEqual(SettingsSnapshot.objects.all().count(), 1)

        with MetricsMock() as mm:
            self.admin.delete_queryset(request, snapshot)
            mm.assert_incr("shepherd.filters.snapshot.delete")
        self.assertEqual(SettingsSnapshot.objects.all().count(), 0)

    @override_settings(STATSD_ENABLED=True)
    def test_publish_snapshot_metrics(self) -> None:
        """Test that publishing snapshot emits metrics."""
        request = mock.Mock()
        request.user = UserFactory()

        SettingsSnapshot.objects.create(
            name="Settings Snapshot",
            settings_type=self.partner,
            json_settings=self.partner.to_dict(),
            created_by=request.user,
        )

        with MetricsMock() as mm:
            publish_snapshot(None, request, SettingsSnapshot.objects.all())
            mm.assert_incr("shepherd.filters.snapshot.upload.success")
            mm.assert_timing("shepherd.filters.snapshot.publish.timer")


class AllocationSettingAdminTest(TestCase):
    """Test class for AllocationSetting."""

    def setUp(self) -> None:
        """Set up objects and variables for testing AllocationSetting."""
        request_factory = RequestFactory()
        self.request = request_factory.get("/admin/consvc_shepherd/allocationsetting/")
        self.request.user = UserFactory()

        with open("./schema/allocation.schema.json", "r") as f:
            self.allocation_schema = json.load(f)

        site = AdminSite()
        self.admin = AllocationSettingAdmin(AllocationSetting, site)

        allocations: dict[str, Any] = {}
        allocations.update({"name": "SOV-20230101140000", "allocations": []})

        amp_partner: Partner = Partner.objects.create(name="amp")
        moz_partner: Partner = Partner.objects.create(name="moz_sales")
        position1_alloc: AllocationSetting = AllocationSetting.objects.create(
            position=1
        )
        PartnerAllocation.objects.create(
            allocation_position=position1_alloc, partner=amp_partner, percentage=100
        )
        PartnerAllocation.objects.create(
            allocation_position=position1_alloc, partner=moz_partner, percentage=0
        )

        position2_alloc: AllocationSetting = AllocationSetting.objects.create(
            position=2
        )
        PartnerAllocation.objects.create(
            allocation_position=position2_alloc, partner=amp_partner, percentage=85
        )
        PartnerAllocation.objects.create(
            allocation_position=position2_alloc, partner=moz_partner, percentage=15
        )

        mock_storage_open = mock.patch(
            "django.core.files.storage.default_storage." "open"
        )
        self.mock_storage_open = mock_storage_open.start()
        self.addCleanup(self.mock_storage_open.stop)

    def test_publish_allocation(self) -> None:
        """Test that publish action of allocation settings calls send_to_storage."""
        request = mock.Mock()
        publish_allocation(None, request, AllocationSetting.objects.all())
        self.mock_storage_open.assert_called()


    def test_insufficient_positions_results_in_no_publish(self) -> None:
        """Test that publish action with insufficient allocation
        does not call send_to_storage.
        """
        request = mock.Mock()
        publish_allocation(None, request, AllocationSetting.objects.filter(position=1))
        self.mock_storage_open.assert_not_called()
    
    @override_settings(STATSD_ENABLED=True)
    def test_publish_allocation_metrics(self) -> None:
        """Test that publish action of allocation settings emits metrics."""
        request = mock.Mock()

        with MetricsMock() as mm:
            publish_allocation(None, request, AllocationSetting.objects.all())
            mm.assert_incr("shepherd.allocation.upload.success")
            mm.assert_timing("shepherd.allocation.publish.timer")

    @override_settings(STATSD_ENABLED=True)
    def test_delete_allocation(self) -> None:
        """Test that delete_queryset removes AllocationSetting."""
        request = mock.Mock()
        request.user = UserFactory()

        self.assertEqual(AllocationSetting.objects.all().count(), 2)

        allocation_setting_2 = AllocationSetting.objects.get(position=2)
        self.admin.delete_queryset(request, allocation_setting_2)
        self.assertEqual(AllocationSetting.objects.all().count(), 1)


