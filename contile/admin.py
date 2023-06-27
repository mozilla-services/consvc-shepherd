"""Admin module for consvc_shepherd/contile."""
from django import forms
from django.contrib import admin
from django.shortcuts import render
from django.urls import path

from consvc_shepherd.utils import ShepherdMetrics
from contile.models import Advertiser, AdvertiserUrl, Partner

metrics = ShepherdMetrics("shepherd")


class CsvImportForm(forms.Form):
    """CSV Import Form"""

    csv_upload = forms.FileField()


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

    def get_urls(self):
        """Create new path to upload-csv"""
        urls = super().get_urls()
        new_urls = [path("upload-csv/", self.upload_csv)]
        return new_urls + urls

    def upload_csv(self, request):
        """Render function for new csv endpoint."""
        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)


@admin.register(Partner)
class PartnerListAdmin(admin.ModelAdmin):
    """The PartnerList Admin Model."""

    model = Partner
    ordering = ["name"]
    metrics.incr("partner.create")
