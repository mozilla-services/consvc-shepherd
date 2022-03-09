from consvc_shepherd.models import Advertiser, AdvertiserUrl, SettingsSnapshot
from consvc_shepherd.storage import send_to_storage
from django.contrib import admin, messages
from django import forms
import json


@admin.action(description='Publish Settings Snapshot')
def publish_snapshot(modeladmin, request, queryset):

    # TODO this doesn't intake advertisers at the moment
    if len(queryset) > 1:
        messages.error(request,
                       "Only 1 snapshot can be published at the same time")
    else:
        snapshot = queryset[0]
        snapshot.launched_by = request.user
        content = json.dumps(snapshot.json(), indent=2)
        send_to_storage(snapshot.name, content)
        snapshot.save()
        messages.info(request, 'Snapshot has been published')


@admin.register(SettingsSnapshot)
class ModelAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "launched_by")
    readonly_fields = ["created_by", "launched_by"]
    actions = [publish_snapshot]

    def save_model(self, request, obj, form, change) -> None:
        obj.created_by = request.user
        super(ModelAdmin, self).save_model(request, obj, form, change)


class AdUrlInlineForm(forms.ModelForm):
    class Meta:
        model = AdvertiserUrl
        widgets = {"matching": forms.RadioSelect}
        fields = "__all__"


class AdUrlInline(admin.TabularInline):
    extra = 1
    model = AdvertiserUrl
    form = AdUrlInlineForm




@admin.register(Advertiser)
class AdvertiserListAdmin(admin.ModelAdmin):
    model = Advertiser
    inlines = [AdUrlInline]
