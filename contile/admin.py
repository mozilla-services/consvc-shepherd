"""Admin module for consvc_shepherd/contile."""
from django import forms
from django.contrib import admin

from consvc_shepherd.utils import ShepherdMetrics
from contile.models import Advertiser, AdvertiserUrl, Partner

metrics = ShepherdMetrics("shepherd")


class AdUrlInlineForm(forms.ModelForm):
    """Model Form Ad Url Inline Form Model."""

    class Meta:
        """Meta class for AdvertiserUrl AdUrlInlineForm."""

        model = AdvertiserUrl
        widgets = {"matching": forms.RadioSelect}
        fields = "__all__"


class AdUrlInline(admin.TabularInline):
    """Tabular Inline Ad Url Inline Model."""

    extra = 1
    model = AdvertiserUrl
    form = AdUrlInlineForm


@admin.register(Advertiser)
class AdvertiserListAdmin(admin.ModelAdmin):
    """Registration of AdvertiserListAdmin for Advertiser Model."""

    model = Advertiser
    inlines = [AdUrlInline]
    ordering = ["name"]


@admin.register(Partner)
class PartnerListAdmin(admin.ModelAdmin):
    """The PartnerList Admin Model."""

    model = Partner
    ordering = ["name"]
    metrics.incr("partner.create")
