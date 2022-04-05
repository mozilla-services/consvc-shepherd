from django import forms
from django.contrib import admin
from django.contrib.postgres.forms import SimpleArrayField

from contile.models import Advertiser, AdvertiserUrl, Partner


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
