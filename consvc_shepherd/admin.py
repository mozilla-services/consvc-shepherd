import json

from django import forms
from django.contrib import admin, messages
from django.contrib.postgres.forms import SimpleArrayField
from django.utils import timezone

from consvc_shepherd.models import Advertiser, AdvertiserUrl, Partner, SettingsSnapshot
from consvc_shepherd.storage import send_to_storage


@admin.action(description="Publish Settings Snapshot")
def publish_snapshot(modeladmin, request, queryset):
    # TODO this doesn't intake advertisers at the moment
    if len(queryset) > 1:
        messages.error(request, "Only 1 snapshot can be published at the same time")
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
    readonly_fields = ["created_by", "launched_by", "launched_date"]
    actions = [publish_snapshot]

    def save_model(self, request, obj, form, change) -> None:
        obj.created_by = request.user
        super(ModelAdmin, self).save_model(request, obj, form, change)


class AdUrlInlineForm(forms.ModelForm):
    class Meta:
        model = AdvertiserUrl
        widgets = {"matching": forms.RadioSelect}
        fields = "__all__"


class PartnerForm(forms.ModelForm):
    click_hosts = SimpleArrayField(
        forms.CharField(),
        label="Click Hosts (list by separated commas)",
        required=False,
    )
    impression_hosts = SimpleArrayField(
        forms.CharField(),
        label="Impression Hosts (list by separated commas)",
        required=False,
    )


class AdUrlInline(admin.TabularInline):
    extra = 1
    model = AdvertiserUrl
    form = AdUrlInlineForm


@admin.register(Advertiser)
class AdvertiserListAdmin(admin.ModelAdmin):
    model = Advertiser
    inlines = [AdUrlInline]


@admin.register(Partner)
class PartnerListAdmin(admin.ModelAdmin):
    model = Partner
    form = PartnerForm
