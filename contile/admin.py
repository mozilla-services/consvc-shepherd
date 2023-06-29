"""Admin module for consvc_shepherd/contile."""

from django import forms
from django.contrib import admin, messages
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

    def get_urls(self):  # pragma: no cover
        """Create new path to upload-csv"""
        urls = super().get_urls()
        new_urls = [path("upload-csv/", self.upload_csv)]
        return new_urls + urls

    def upload_csv(self, request):  # pragma: no cover
        """Render function for new csv endpoint."""
        form = CsvImportForm()
        data = {"form": form}
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            csv_data = [
                entry.decode("utf-8").strip("\r\n") for entry in csv_file.readlines()
            ][2:]
            advertisers = {}
            advertiser = ""
            for entry in csv_data:
                line = entry.split(",")
                if line[0] != "":
                    advertiser = line[0]
                    advertisers[advertiser] = []
                if line[0] in advertisers and line[3]:
                    advertisers[advertiser].append(
                        {
                            "iso": line[2],
                            "root_domain": line[3].strip().replace('"', ""),
                            "incl_filter_root": line[4],
                            "path_var": line[5].strip().replace('"', ""),
                            "incl_filter_path_var": line[6],
                            "last_updated_adm": line[7],
                            "updated_by": line[8],
                        }
                    )
                elif not line[0] and line[3]:
                    advertisers[advertiser].append(
                        {
                            "iso": line[2],
                            "root_domain": line[3].strip().replace('"', ""),
                            "incl_filter_root": line[4],
                            "path_var": line[5].strip().replace('"', ""),
                            "incl_filter_path_var": line[6],
                            "last_updated_adm": line[7],
                            "updated_by": line[8],
                        }
                    )
            for adv_name, settings in advertisers.items():
                if settings != []:
                    print(adv_name, settings)
                    advertiser = Advertiser.objects.create(
                        name=adv_name, partner=Partner.objects.filter(name="adm")[0]
                    )
                    for entry in settings:

                        path = entry["path_var"].strip('"').strip()
                        if not path:
                            path = "/"
                        advertiser_url = AdvertiserUrl.objects.create(  # noqa
                            advertiser=advertiser,
                            geo=entry["iso"],
                            domain=entry["root_domain"].strip('"'),
                            path=path,
                            matching=True,
                        )

        messages.info(request, "Advertisers successfully uploaded!")
        return render(request, "admin/csv_upload.html", data)


@admin.register(Partner)
class PartnerListAdmin(admin.ModelAdmin):
    """The PartnerList Admin Model."""

    model = Partner
    ordering = ["name"]
    metrics.incr("partner.create")
