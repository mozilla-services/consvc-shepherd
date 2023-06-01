"""Admin module for consvc_shepherd."""
import json

from django.conf import settings
from django.contrib import admin, messages
from django.utils import dateformat, timezone
from jsonschema import exceptions, validate

from consvc_shepherd.forms import AllocationSettingForm, PartnerAllocationForm
from consvc_shepherd.models import (
    AllocationSetting,
    PartnerAllocation,
    SettingsSnapshot,
)
from consvc_shepherd.storage import send_to_storage
from consvc_shepherd.utils import ShepherdMetrics

metrics: ShepherdMetrics = ShepherdMetrics("shepherd")


@admin.action(description="Publish Settings Snapshot")
@metrics.time_if_enabled("snapshot.publish.timer")
def publish_snapshot(modeladmin, request, queryset):
    """Publish advertiser snapshot."""
    if len(queryset) > 1:
        messages.error(request, "Only 1 snapshot can be published at the same time")
    elif queryset[0].launched_date is not None:
        messages.error(
            request,
            "Snapshot has already been launched, create a new snapshot to launch",
        )
    else:
        snapshot = queryset[0]
        snapshot.launched_by = request.user
        snapshot.launched_date = timezone.now()
        content = json.dumps(snapshot.json_settings, indent=2)
        with open("./schema/adm_filter.schema.json", "r") as f:
            settings_schema = json.load(f)
            try:
                validate(snapshot.json_settings, schema=settings_schema)
                send_to_storage(content, settings.GS_BUCKET_FILE_NAME)
                snapshot.save()
                metrics.incr_if_enabled("snapshot.upload.success")
                messages.info(request, "Snapshot has been published.")
            except exceptions.ValidationError:
                metrics.incr_if_enabled("snapshot.schema.validation.fail")
                messages.error(
                    request,
                    "JSON generated is different from the expected snapshot schema.",
                )


@admin.action(description="Publish Allocation")
@metrics.time_if_enabled("allocation.publish.timer")
def publish_allocation(modeladmin, request, queryset) -> None:
    """Publish allocation JSON settings."""
    allocation_request = queryset.order_by("position")
    if AllocationSetting.objects.count() != len(queryset):
        messages.warning(request, "Warning: Not all allocation settings were selected.")

    allocation_settings_name: str = f"SOV-{dateformat.format(timezone.now(), 'YmdHis')}"
    allocation: dict = {
        "name": allocation_settings_name,
        "allocations": [allocation.to_dict() for allocation in allocation_request],
    }

    with open("./schema/allocation.schema.json", "r") as f:
        allocation_schema = json.load(f)
        try:
            validate(allocation, schema=allocation_schema)
            allocation_json = json.dumps(allocation, indent=2)
            send_to_storage(allocation_json, settings.ALLOCATION_FILE_NAME)
            metrics.incr_if_enabled("allocation.upload.success")
            messages.info(request, "Allocation setting has been published.")
        except exceptions.ValidationError:
            metrics.incr_if_enabled("allocation.schema.validation.fail")
            messages.error(
                request,
                "JSON generated is different from the expected allocation schema.",
            )


@admin.register(SettingsSnapshot)
class ModelAdmin(admin.ModelAdmin):
    """Registration of SettingsSnapshot."""

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
        super(ModelAdmin, self).save_model(request, obj, form, change)
        metrics.incr_if_enabled("snapshot.create")

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
        metrics.incr_if_enabled("snapshot.delete")
        queryset.delete()


class PartnerAllocationInline(admin.TabularInline):
    """PartnerAllocationInline TabularInline child model."""

    extra = 1
    model = PartnerAllocation
    form = PartnerAllocationForm


@admin.register(AllocationSetting)
class AllocationSettingAdmin(admin.ModelAdmin):
    """Registration of AllocationSetting."""

    model = AllocationSetting
    inlines = [PartnerAllocationInline]
    form = AllocationSettingForm
    actions = [publish_allocation]

    def delete_queryset(self, request, queryset) -> None:
        """Delete given AllocationSetting entry."""
        metrics.incr_if_enabled("allocation.delete")
        queryset.delete()
