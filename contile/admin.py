from django import forms
from django.contrib import admin, messages

from contile.models import Advertiser, AdvertiserUrl, Partner


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


@admin.register(Partner)
class PartnerListAdmin(admin.ModelAdmin):
    model = Partner

    def delete_queryset(self, request, queryset):
        super(PartnerListAdmin, self).delete_queryset(request, queryset)
        messages.warning(
            request,
            "Please ensure SOV allocation percentages are adjusted to account for the deleted Partner.",
        )
