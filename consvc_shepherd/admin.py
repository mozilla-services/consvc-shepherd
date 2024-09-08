"""Admin module for consvc_shepherd."""

import json

from django.conf import settings
from django.contrib import admin, messages
from django.utils import dateformat, timezone
from jsonschema import exceptions, validate

from consvc_shepherd.forms import AllocationSettingForm, AllocationSettingFormset
from consvc_shepherd.models import (
    AllocationSetting,
    AllocationSettingsSnapshot,
    BoostrDeal,
    BoostrDealProduct,
    BoostrProduct,
    BoostrSyncStatus,
    PartnerAllocation,
    SettingsSnapshot,
)
from consvc_shepherd.storage import send_to_storage
from consvc_shepherd.utils import ShepherdMetrics

metrics: ShepherdMetrics = ShepherdMetrics("shepherd")


@admin.action(description="Publish Settings Snapshot")
@metrics.timer("filters.snapshot.publish.timer")
def publish_snapshot(modeladmin, request, queryset):
    """Publish advertiser snapshot."""
    match list(queryset):
        case [snapshot] if snapshot.launched_date is not None:
            messages.error(
                request,
                "Snapshot has already been launched, create a new snapshot to launch",
            )
        case [snapshot]:
            snapshot.launched_by = request.user
            snapshot.launched_date = timezone.now()
            content = json.dumps(snapshot.json_settings, indent=2)
            with open("./schema/adm_filter.schema.json", "r") as f:
                settings_schema = json.load(f)
            try:
                validate(snapshot.json_settings, schema=settings_schema)
                metrics.incr("filters.snapshot.schema.validation.success")
                send_to_storage(content, settings.GS_BUCKET_FILE_NAME)
                snapshot.save()
                metrics.incr("filters.snapshot.upload.success")
                messages.info(request, "Snapshot has been published.")
            except exceptions.ValidationError:
                metrics.incr("filters.snapshot.schema.validation.fail")
                messages.error(
                    request,
                    "JSON generated is different from the expected snapshot schema.",
                )
        case _:  # queryset is either empty or has more than 1 entry
            messages.error(request, "Only 1 snapshot can be published at the same time")


@admin.action(description="Publish Allocation")
@metrics.timer("allocation.publish.timer")
def publish_allocation(modeladmin, request, queryset) -> None:
    """Publish allocation JSON settings."""
    match list(queryset):
        case [snapshot] if snapshot.launched_date is not None:
            messages.error(
                request,
                "Allocation Snapshot has already been launched, create a new snapshot to launch",
            )
        case [snapshot]:
            json_settings = snapshot.json_settings
            with open("./schema/allocation.schema.json", "r") as f:
                allocation_schema = json.load(f)
                try:
                    validate(json_settings, schema=allocation_schema)
                    metrics.incr("allocation.schema.validation.success")
                    allocation_json = json.dumps(json_settings, indent=2)
                    send_to_storage(allocation_json, settings.ALLOCATION_FILE_NAME)
                    snapshot.launched_date = timezone.now()
                    snapshot.save()
                    metrics.incr("allocation.upload.success")
                    messages.info(request, "Allocation setting has been published.")
                except exceptions.ValidationError:
                    metrics.incr("allocation.schema.validation.fail")
                    messages.error(
                        request,
                        "JSON generated is different from the expected allocation schema. "
                        "Ensure that there are two allocation settings selected",
                    )
        case _:
            messages.error(request, "Only 1 snapshot can be published at the same time")


@admin.register(SettingsSnapshot)
class SettingsSnapshotModelAdmin(admin.ModelAdmin):
    """Admin model for Settings Snapshot."""

    list_display: tuple[str, str, str, str] = (
        "name",
        "created_by",
        "launched_by",
        "launched_date",
    )
    readonly_fields: list[str] = [
        "json_settings",
        "created_by",
        "launched_by",
        "launched_date",
    ]
    actions: list = [publish_snapshot]

    def save_model(self, request, obj, form, change) -> None:
        """Save SettingsSnapshot model instance."""
        json_settings = obj.settings_type.to_dict()
        obj.json_settings = json_settings
        obj.created_by = request.user
        super(SettingsSnapshotModelAdmin, self).save_model(request, obj, form, change)
        metrics.incr("filters.snapshot.create")

    def get_readonly_fields(self, request, obj=None) -> list:
        """Return list of read-only fields for SettingsSnapshot."""
        if obj:
            return ["name", "settings_type"] + self.readonly_fields
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None) -> bool:
        """Return boolean of object's delete permissions."""
        return not (obj and obj.launched_by and obj.launched_date)

    def delete_queryset(self, request, queryset) -> None:
        """Delete given SettingsSnapshot entry."""
        super(SettingsSnapshotModelAdmin, self).delete_queryset(request, queryset)
        metrics.incr("filters.snapshot.delete")


@admin.register(AllocationSettingsSnapshot)
class AllocationSettingsSnapshotModelAdmin(admin.ModelAdmin):
    """Admin model for AllocationSettingsSnapshot."""

    list_display: tuple[str, str, str, str] = (
        "name",
        "created_by",
        "launched_by",
        "launched_date",
    )
    readonly_fields: list[str] = [
        "json_settings",
        "created_by",
        "launched_by",
        "launched_date",
    ]
    actions: list = [publish_allocation]

    def save_model(self, request, obj, form, change) -> None:
        """Save SettingsSnapshot model instance."""
        allocation_settings_name: str = (
            f"SOV-{dateformat.format(timezone.now(), 'YmdHis')}"
        )
        json_settings: dict = {
            "name": allocation_settings_name,
            "allocations": [
                allocation.to_dict()
                for allocation in AllocationSetting.objects.all().order_by("position")
            ],
        }
        obj.json_settings = json_settings
        obj.created_by = request.user
        super(AllocationSettingsSnapshotModelAdmin, self).save_model(
            request, obj, form, change
        )
        metrics.incr("allocations.snapshot.create")

    def get_readonly_fields(self, request, obj=None) -> list:
        """Return list of read-only fields for SettingsSnapshot."""
        return ["name", *self.readonly_fields] if obj else self.readonly_fields

    def has_delete_permission(self, request, obj=None) -> bool:
        """Return boolean of object's delete permissions."""
        return not (obj and obj.launched_by and obj.launched_date)

    def delete_queryset(self, request, queryset) -> None:
        """Delete given SettingsSnapshot entry."""
        super(AllocationSettingsSnapshotModelAdmin, self).delete_queryset(
            request, queryset
        )
        metrics.incr("allocations.snapshot.delete")


class PartnerAllocationInline(admin.TabularInline):
    """PartnerAllocationInline TabularInline child model."""

    extra = 1
    model = PartnerAllocation
    formset = AllocationSettingFormset


@admin.register(AllocationSetting)
class AllocationSettingAdmin(admin.ModelAdmin):
    """Registration of AllocationSetting."""

    model = AllocationSetting
    inlines = [PartnerAllocationInline]
    form = AllocationSettingForm
    list_display = ["position", "partner_allocation"]
    ordering = ["position"]

    def partner_allocation(self, obj) -> str:  # pragma: no cover
        """Partner allocation summary display column."""
        result = PartnerAllocation.objects.filter(allocation_position=obj).order_by(
            "-percentage"
        )
        row = ""
        for item in result:
            if not item.partner:
                row += f"Deleted Partner: {item.percentage}% "
            else:
                row += f"{item.partner.name}: {item.percentage}% "
        return row

    def delete_queryset(self, request, queryset) -> None:
        """Delete given AllocationSetting entry."""
        super(AllocationSettingAdmin, self).delete_queryset(request, queryset)
        metrics.incr("allocation.delete")


class BoostrDealProductInline(admin.StackedInline):
    """BoostrDealProductInline is for displaying products and their budgets in the Deal form"""

    model = BoostrDealProduct
    extra = 0


@admin.register(BoostrDeal)
class BoostrDealAdmin(admin.ModelAdmin):
    """Admin model for sales deals imported from Boostr"""

    model = BoostrDeal
    date_hierarchy = "start_date"
    inlines = [
        BoostrDealProductInline,
    ]
    search_fields = ["boostr_id", "name", "advertiser", "sales_representatives"]
    search_help_text = "Search by boostr id, name, adversiter, or sales reps"
    list_filter = [
        "currency",
        "start_date",
        ("products", admin.RelatedOnlyFieldListFilter),
    ]
    list_display = [
        "boostr_id",
        "name",
        "advertiser",
        "currency",
        "amount",
        "start_date",
        "end_date",
        "sales_representatives",
    ]


@admin.register(BoostrProduct)
class BoostrProductAdmin(admin.ModelAdmin):
    """Admin model for sales products imported from Boostr. Deals are many-to-many with products"""

    model = BoostrProduct
    list_display = [
        "boostr_id",
        "full_name",
        "campaign_type",
    ]


@admin.register(BoostrSyncStatus)
class BoostrSyncStatusAdmin(admin.ModelAdmin):
    """Admin model for BoostrSyncStatuss records which represent the status of each Boostr sync operation"""

    model = BoostrSyncStatus
    list_display = [
        "id",
        "synced_on",
        "status",
        "message",
    ]
