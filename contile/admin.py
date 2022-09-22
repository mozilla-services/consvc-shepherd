from django import forms
from django.contrib import admin, messages
from django.contrib.postgres.forms import SimpleArrayField

from contile.models import Advertiser, AdvertiserUrl, Partner


class AdUrlInlineForm(forms.ModelForm):
    class Meta:
        model = AdvertiserUrl
        widgets = {"matching": forms.RadioSelect}
        fields = "__all__"


@admin.action(description="Approve Partner Settings")
def approve_partner_settings(modeladmin, request, queryset):
    if len(queryset) > 1:
        messages.error(request, "Only 1 partner can be approved at a time")
    else:
        partner = queryset[0]
        if partner.last_updated_by != request.user:
            partner.is_active = True
            partner.last_approved_by = request.user
            partner.save()
            messages.info(request, f"Partner: {partner.name} has been approved")
        else:
            messages.error(
                request,
                "This change can't be approved by the same editor, please get another reviewer for approval",
            )


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
    is_active = forms.BooleanField()
    last_updated_by = forms.CharField()
    last_approved_by = forms.CharField()


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
    readonly_fields = ["is_active", "last_updated_by", "last_approved_by"]
    model = Partner
    form = PartnerForm
    actions = [approve_partner_settings]

    def save_model(self, request, obj, form, change):
        obj.is_active = False
        obj.last_updated_by = request.user
        obj.last_approved_by = None
        super(PartnerListAdmin, self).save_model(request, obj, form, change)
