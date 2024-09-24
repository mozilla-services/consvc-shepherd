"""Admin test module for consvc_shepherd."""

import json
from datetime import datetime, timedelta
from typing import Any

import mock
import pytz
from dateutil.relativedelta import relativedelta
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from jsonschema import validate
from markus.testing import MetricsMock

from consvc_shepherd.admin import (
    AllocationSettingsSnapshotModelAdmin,
    SettingsSnapshotModelAdmin,
    publish_allocation,
    publish_snapshot,
)
from consvc_shepherd.models import (
    AllocationSetting,
    AllocationSettingsSnapshot,
    BoostrDeal,
    BoostrDealProduct,
    BoostrProduct,
    Campaign,
    DeliveredFlight,
    Partner,
    PartnerAllocation,
    SettingsSnapshot,
)
from consvc_shepherd.tests.factories import AdminUserFactory, UserFactory
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
        self.admin = SettingsSnapshotModelAdmin(SettingsSnapshot, site)

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
        timestamp = datetime(2022, 1, 11, 1, 15, 12, tzinfo=pytz.utc)
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


class AllocationSettingsSnapshotAdminTest(TestCase):
    """Test class for AllocationSetting."""

    def setUp(self) -> None:
        """Set up objects and variables for testing AllocationSetting."""
        request_factory = RequestFactory()
        self.request = request_factory.get("/admin/consvc_shepherd/allocationsetting/")
        self.request.user = UserFactory()

        with open("./schema/allocation.schema.json", "r") as f:
            self.allocation_schema = json.load(f)

        site = AdminSite()
        self.admin = AllocationSettingsSnapshotModelAdmin(AllocationSetting, site)

        self.allocations_dict: dict[str, Any] = {
            "name": "SOV-20230101140000",
            "allocations": [],
        }

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

    def test_save_model_generates_json(self) -> None:
        """Test that snapshot value matches expected json object."""
        self.assertEqual(AllocationSettingsSnapshot.objects.all().count(), 0)
        self.allocations_dict["allocations"] = [
            allocation.to_dict() for allocation in AllocationSetting.objects.all()
        ]

        self.admin.save_model(
            self.request,
            AllocationSettingsSnapshot(name="snapshot1"),
            None,
            {},
        )

        self.assertEqual(AllocationSettingsSnapshot.objects.all().count(), 1)
        snapshot = AllocationSettingsSnapshot.objects.all().first()
        if snapshot:
            validate(snapshot.json_settings, schema=self.allocation_schema)
            self.assertEqual(
                snapshot.json_settings["allocations"],
                self.allocations_dict["allocations"],
            )

    def test_publish_snapshot_does_not_launch_already_launch_snapshot(self) -> None:
        """Test that publish snapshot action does not launch pre-existing snapshot."""
        request = mock.Mock()
        request.user = UserFactory()
        timestamp = datetime(2023, 5, 19, 1, 15, 12, tzinfo=pytz.utc)

        AllocationSettingsSnapshot.objects.create(
            name="Settings Snapshot",
            created_by=request.user,
            launched_date=timestamp,
            launched_by=request.user,
            json_settings=self.allocations_dict,
        )
        publish_snapshot(None, request, AllocationSettingsSnapshot.objects.all())
        snapshots = AllocationSettingsSnapshot.objects.filter(
            launched_date=timezone.now(),
            launched_by=request.user,
        )
        self.assertEqual(len(snapshots), 0)

    def test_publish_allocation(self) -> None:
        """Test that publish action of allocation settings calls send_to_storage."""
        self.allocations_dict["allocations"] = [
            allocation.to_dict() for allocation in AllocationSetting.objects.all()
        ]
        AllocationSettingsSnapshot.objects.create(
            name="snapshot1", json_settings=self.allocations_dict
        )
        request = mock.Mock()
        publish_allocation(None, request, AllocationSettingsSnapshot.objects.all())
        self.mock_storage_open.assert_called()

    def test_insufficient_positions_results_in_no_publish(self) -> None:
        """Test that publish action with insufficient allocation
        does not call send_to_storage.
        """
        self.allocations_dict["allocations"] = [
            allocation.to_dict()
            for allocation in AllocationSetting.objects.filter(position=1)
        ]
        AllocationSettingsSnapshot.objects.create(
            name="snapshot1", json_settings=self.allocations_dict
        )
        request = mock.Mock()
        publish_allocation(None, request, AllocationSettingsSnapshot.objects.all())
        self.mock_storage_open.assert_not_called()

    @override_settings(STATSD_ENABLED=True)
    def test_publish_allocation_metrics(self) -> None:
        """Test that publish action of allocation settings emits metrics."""
        self.allocations_dict["allocations"] = [
            allocation.to_dict() for allocation in AllocationSetting.objects.all()
        ]
        AllocationSettingsSnapshot.objects.create(
            name="snapshot1", json_settings=self.allocations_dict
        )
        request = mock.Mock()

        with MetricsMock() as mm:
            publish_allocation(None, request, AllocationSettingsSnapshot.objects.all())
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


@override_settings(DEBUG=True)
class CampaignAdminTests(TestCase):
    """Test case for the admin interface of Campaign."""

    def setUp(self):
        """Set up test user, request, and data."""
        self.request_factory = RequestFactory()
        self.admin_user = AdminUserFactory()

        self.create_test_data()

    def create_test_data(self):
        """Create test data for BoostrDeal, BoostrProduct, and Campaign models."""
        self.deal1 = BoostrDeal.objects.create(
            boostr_id=1,
            name="Test Deal1",
            advertiser="Test Advertiser1",
            currency="$",
            amount=10000,
            sales_representatives="Rep1, Rep2",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        self.deal2 = BoostrDeal.objects.create(
            boostr_id=2,
            name="Test Deal2",
            advertiser="Test Advertiser2",
            currency="$",
            amount=10000,
            sales_representatives="Rep1, Rep2",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        # Create BoostrProduct instances
        self.product1 = BoostrProduct.objects.create(
            boostr_id=1, full_name="Product 1", country="US", campaign_type="CPC"
        )
        self.product2 = BoostrProduct.objects.create(
            boostr_id=2, full_name="Product 2", country="CA", campaign_type="CPM"
        )

        # Create BoostrDealProduct instances linking to the products
        self.deal_product1 = BoostrDealProduct.objects.create(
            boostr_deal=self.deal1,
            boostr_product=self.product1,
            budget=5000,
            month="2024-01",
        )
        self.deal_product2 = BoostrDealProduct.objects.create(
            boostr_deal=self.deal2,
            boostr_product=self.product2,
            budget=5000,
            month="2024-02",
        )

        # Create Campaign instances linked to the BoostrDeal
        self.campaign_overview1 = Campaign.objects.create(
            deal=self.deal1,
            ad_ops_person="AdOps Person 1",
            notes="Notes 1",
            kevel_flight_id=1001,
            net_spend=1000,
            impressions_sold=2000,
            start_date="2023-01-01",
            end_date="2023-01-05",
        )
        self.campaign_overview2 = Campaign.objects.create(
            deal=self.deal2,
            ad_ops_person="AdOps Person 2",
            notes="Notes 2",
            kevel_flight_id=1002,
            net_spend=1500,
            impressions_sold=3000,
            start_date="2023-01-01",
            end_date="2023-01-05",
        )

    def test_month_filter(self):
        """Test filtering Campaign by month."""
        response = self.client.get(
            reverse("admin:consvc_shepherd_campaign_changelist") + "?month=2024-01",
            **{"settings.OPENIDC_HEADER": "dev@example.com"},
        )
        self.assertContains(response, "AdOps Person 1")
        self.assertNotContains(response, "AdOps Person 2")

    def test_placement_filter(self):
        """Test filtering Campaign by placement."""
        response = self.client.get(
            reverse("admin:consvc_shepherd_campaign_changelist")
            + "?placement=Product 2",
            **{"settings.OPENIDC_HEADER": "dev@example.com"},
        )
        self.assertContains(response, "AdOps Person 2")
        self.assertNotContains(response, "AdOps Person 1")

    def test_country_filter(self):
        """Test filtering Campaign by country."""
        response = self.client.get(
            reverse("admin:consvc_shepherd_campaign_changelist") + "?country=CA",
            **{"settings.OPENIDC_HEADER": "dev@example.com"},
        )
        self.assertContains(response, "AdOps Person 2")
        self.assertNotContains(response, "AdOps Person 1")

    def test_deal_advertiser_filter(self):
        """Test changelist_view with deal advertiser filter applied."""
        response = self.client.get(
            reverse("admin:consvc_shepherd_campaign_changelist")
            + "?deal__advertiser=Test Advertiser1",
            **{"settings.OPENIDC_HEADER": "dev@example.com"},
        )
        self.assertContains(response, "AdOps Person 1")
        self.assertNotContains(response, "AdOps Person 2")


@override_settings(DEBUG=True)
class DeliveredFlightAdminTests(TestCase):
    """Test case for the admin interface of DeliveredFlight."""

    def setUp(self):
        """Set up test user, request, and data."""
        self.request_factory = RequestFactory()
        self.admin_user = AdminUserFactory()

        self.create_test_data()

    def create_test_data(self):
        """Create test data for Delivered Flight model."""
        self.delivered_flight1 = DeliveredFlight.objects.create(
            submission_date=timezone.now(),
            campaign_id=12345,
            campaign_name="Campaign Name 1",
            flight_id=54321,
            flight_name="Flight Name 1",
            country="US",
            provider="Partner 1",
            clicks_delivered=100,
            impressions_delivered=1000,
        )

        self.delivered_flight2 = DeliveredFlight.objects.create(
            submission_date=timezone.now() - relativedelta(months=1),
            campaign_id=55555,
            campaign_name="Campaign Name 2",
            flight_id=88888,
            flight_name="Flight Name 2",
            country="BR",
            provider="Partner 2",
            clicks_delivered=50,
            impressions_delivered=500,
        )

    def test_partner_filter(self):
        """Test filtering Delivered Flight by partner name."""
        response = self.client.get(
            reverse("admin:consvc_shepherd_deliveredflight_changelist")
            + "?partner=Partner1",
            **{"settings.OPENIDC_HEADER": "dev@example.com"},
        )

        self.assertContains(response, "Partner1")
        self.assertNotContains(response, "Partner2")

    def test_submission_date_filter(self):
        """Test filtering Delivered Flight by submission date."""
        # Get today's date at 00:00 AM and 11:59 PM
        today_start = timezone.now().date()
        today_end = today_start + timedelta(days=1)

        # Construct the filter parameters
        filter_params = {
            "submission_date__gte": today_start,
            "submission_date__lt": today_end,
        }

        # Construct the URL with filter parameters
        url = reverse("admin:consvc_shepherd_deliveredflight_changelist")

        # Use the filter_params in the GET request
        response = self.client.get(
            url, data=filter_params, **{"settings.OPENIDC_HEADER": "dev@example.com"}
        )

        # Check if the response contains today's delivered flight
        self.assertContains(response, self.delivered_flight1.provider)
        # Ensure it does not contain the delivered flight from last month
        self.assertNotContains(response, self.delivered_flight2.provider)
