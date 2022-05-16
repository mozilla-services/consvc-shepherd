import json

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone

from consvc_shepherd.models import SettingsSnapshot
from consvc_shepherd.storage import send_to_storage


@admin.action(description="Publish Settings Snapshot")
def publish_snapshot(modeladmin, request, queryset):
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
        send_to_storage(snapshot.name, content)
        snapshot.save()
        messages.info(request, "Snapshot has been published")


@admin.register(SettingsSnapshot)
class ModelAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "launched_by", "launched_date")
    readonly_fields = ["json_settings", "created_by", "launched_by", "launched_date"]
    actions = [publish_snapshot]

    def save_model(self, request, obj, form, change) -> None:
        if obj.settings_type.is_active:
            json_settings = obj.settings_type.to_dict()
            obj.json_settings = json_settings
            obj.created_by = request.user
            super(ModelAdmin, self).save_model(request, obj, form, change)
        else:
            raise ValidationError("Partner Selected is not active")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["name", "settings_type"] + self.readonly_fields
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return not (obj and obj.launched_by and obj.launched_date)
