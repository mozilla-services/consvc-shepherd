"""Admin module for consvc_shepherd."""

import json

from django.conf import settings
from django.contrib import admin, messages
from django.db.models import FloatField, OuterRef, Subquery, Sum
from django.utils import dateformat, timezone
from django.utils.translation import gettext_lazy as _
from jsonschema import exceptions, validate

from consvc_shepherd.forms import AllocationSettingForm, AllocationSettingFormset
from consvc_shepherd.models import (
    AllocationSetting,
    AllocationSettingsSnapshot,
    BoostrDeal,
    BoostrDealProduct,
    BoostrProduct,
    CampaignOverview,
    CampaignOverviewSummary,
    PartnerAllocation,
    SettingsSnapshot,
)
from consvc_shepherd.storage import send_to_storage
from consvc_shepherd.utils import ShepherdMetrics

metrics: ShepherdMetrics = ShepherdMetrics("shepherd")


@admin.action(description="Publish Settings Snapshot")
@metrics.timer("filters.snapshot.publish.timer")
def publish_snapshot(modeladmin, request, queryset):
    """Publish advertiser snapshot."""
    match list(queryset):
        case [snapshot] if snapshot.launched_date is not None:
            messages.error(
                request,
                "Snapshot has already been launched, create a new snapshot to launch",
            )
        case [snapshot]:
            snapshot.launched_by = request.user
            snapshot.launched_date = timezone.now()
            content = json.dumps(snapshot.json_settings, indent=2)
            with open("./schema/adm_filter.schema.json", "r") as f:
                settings_schema = json.load(f)
            try:
                validate(snapshot.json_settings, schema=settings_schema)
                metrics.incr("filters.snapshot.schema.validation.success")
                send_to_storage(content, settings.GS_BUCKET_FILE_NAME)
                snapshot.save()
                metrics.incr("filters.snapshot.upload.success")
                messages.info(request, "Snapshot has been published.")
            except exceptions.ValidationError:
                metrics.incr("filters.snapshot.schema.validation.fail")
                messages.error(
                    request,
                    "JSON generated is different from the expected snapshot schema.",
                )
        case _:  # queryset is either empty or has more than 1 entry
            messages.error(request, "Only 1 snapshot can be published at the same time")


@admin.action(description="Publish Allocation")
@metrics.timer("allocation.publish.timer")
def publish_allocation(modeladmin, request, queryset) -> None:
    """Publish allocation JSON settings."""
    match list(queryset):
        case [snapshot] if snapshot.launched_date is not None:
            messages.error(
                request,
                "Allocation Snapshot has already been launched, create a new snapshot to launch",
            )
        case [snapshot]:
            json_settings = snapshot.json_settings
            with open("./schema/allocation.schema.json", "r") as f:
                allocation_schema = json.load(f)
                try:
                    validate(json_settings, schema=allocation_schema)
                    metrics.incr("allocation.schema.validation.success")
                    allocation_json = json.dumps(json_settings, indent=2)
                    send_to_storage(allocation_json, settings.ALLOCATION_FILE_NAME)
                    snapshot.launched_date = timezone.now()
                    snapshot.save()
                    metrics.incr("allocation.upload.success")
                    messages.info(request, "Allocation setting has been published.")
                except exceptions.ValidationError:
                    metrics.incr("allocation.schema.validation.fail")
                    messages.error(
                        request,
                        "JSON generated is different from the expected allocation schema. "
                        "Ensure that there are two allocation settings selected",
                    )
        case _:
            messages.error(request, "Only 1 snapshot can be published at the same time")


@admin.register(SettingsSnapshot)
class SettingsSnapshotModelAdmin(admin.ModelAdmin):
    """Admin model for Settings Snapshot."""

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
        super(SettingsSnapshotModelAdmin, self).save_model(request, obj, form, change)
        metrics.incr("filters.snapshot.create")

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
        super(SettingsSnapshotModelAdmin, self).delete_queryset(request, queryset)
        metrics.incr("filters.snapshot.delete")


@admin.register(AllocationSettingsSnapshot)
class AllocationSettingsSnapshotModelAdmin(admin.ModelAdmin):
    """Admin model for AllocationSettingsSnapshot."""

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
    actions: list = [publish_allocation]

    def save_model(self, request, obj, form, change) -> None:
        """Save SettingsSnapshot model instance."""
        allocation_settings_name: str = (
            f"SOV-{dateformat.format(timezone.now(), 'YmdHis')}"
        )
        json_settings: dict = {
            "name": allocation_settings_name,
            "allocations": [
                allocation.to_dict()
                for allocation in AllocationSetting.objects.all().order_by("position")
            ],
        }
        obj.json_settings = json_settings
        obj.created_by = request.user
        super(AllocationSettingsSnapshotModelAdmin, self).save_model(
            request, obj, form, change
        )
        metrics.incr("allocations.snapshot.create")

    def get_readonly_fields(self, request, obj=None) -> list:
        """Return list of read-only fields for SettingsSnapshot."""
        return ["name", *self.readonly_fields] if obj else self.readonly_fields

    def has_delete_permission(self, request, obj=None) -> bool:
        """Return boolean of object's delete permissions."""
        return not (obj and obj.launched_by and obj.launched_date)

    def delete_queryset(self, request, queryset) -> None:
        """Delete given SettingsSnapshot entry."""
        super(AllocationSettingsSnapshotModelAdmin, self).delete_queryset(
            request, queryset
        )
        metrics.incr("allocations.snapshot.delete")


class PartnerAllocationInline(admin.TabularInline):
    """PartnerAllocationInline TabularInline child model."""

    extra = 1
    model = PartnerAllocation
    formset = AllocationSettingFormset


@admin.register(AllocationSetting)
class AllocationSettingAdmin(admin.ModelAdmin):
    """Registration of AllocationSetting."""

    model = AllocationSetting
    inlines = [PartnerAllocationInline]
    form = AllocationSettingForm
    list_display = ["position", "partner_allocation"]
    ordering = ["position"]

    def partner_allocation(self, obj) -> str:  # pragma: no cover
        """Partner allocation summary display column."""
        result = PartnerAllocation.objects.filter(allocation_position=obj).order_by(
            "-percentage"
        )
        row = ""
        for item in result:
            if not item.partner:
                row += f"Deleted Partner: {item.percentage}% "
            else:
                row += f"{item.partner.name}: {item.percentage}% "
        return row

    def delete_queryset(self, request, queryset) -> None:
        """Delete given AllocationSetting entry."""
        super(AllocationSettingAdmin, self).delete_queryset(request, queryset)
        metrics.incr("allocation.delete")


class BoostrDealProductInline(admin.StackedInline):
    """BoostrDealProductInline is for displaying products and their budgets in the Deal form"""

    model = BoostrDealProduct
    extra = 0


@admin.register(BoostrDeal)
class BoostrDealAdmin(admin.ModelAdmin):
    """Admin model for sales deals imported from Boostr"""

    model = BoostrDeal
    date_hierarchy = "start_date"
    inlines = [
        BoostrDealProductInline,
    ]
    search_fields = ["boostr_id", "name", "advertiser", "sales_representatives"]
    search_help_text = "Search by boostr id, name, adversiter, or sales reps"
    list_filter = [
        "currency",
        "start_date",
        ("products", admin.RelatedOnlyFieldListFilter),
    ]
    list_display = [
        "boostr_id",
        "name",
        "advertiser",
        "currency",
        "amount",
        "start_date",
        "end_date",
        "sales_representatives",
    ]


@admin.register(BoostrProduct)
class BoostrProductAdmin(admin.ModelAdmin):
    """Admin model for sales products imported from Boostr. Deals are many-to-many with products"""

    model = BoostrProduct
    list_display = [
        "boostr_id",
        "full_name",
        "country",
        "campaign_type",
    ]


class MonthFilter(admin.SimpleListFilter):
    """Filter for listing by month."""

    title = _("month")
    parameter_name = "month"

    def lookups(self, request, model_admin):
        """Return a list of distinct months for the filter options."""
        months = BoostrDealProduct.objects.values_list("month", flat=True).distinct()
        return [(month, month) for month in months]

    def queryset(self, request, queryset):
        """Filter the queryset based on the selected month."""
        if self.value():
            return queryset.filter(deal__boostrdealproduct__month=self.value())
        return queryset


class PlacementFilter(admin.SimpleListFilter):
    """Filter for listing by placement."""

    title = _("placement")
    parameter_name = "placement"

    def lookups(self, request, model_admin):
        """Return a list of distinct placements for the filter options."""
        placements = BoostrProduct.objects.values_list(
            "full_name", flat=True
        ).distinct()
        return [(placement, placement) for placement in placements]

    def queryset(self, request, queryset):
        """Filter the queryset based on the selected placement."""
        if self.value():
            return queryset.filter(
                deal__boostrdealproduct__boostr_product__full_name=self.value()
            ).distinct()
        return queryset


class CountryFilter(admin.SimpleListFilter):
    """Filter for listing by country."""

    title = _("country")
    parameter_name = "country"

    def lookups(self, request, model_admin):
        """Return a list of distinct countries for the filter options."""
        countries = BoostrProduct.objects.values_list("country", flat=True).distinct()
        return [(country, country) for country in countries]

    def queryset(self, request, queryset):
        """Filter the queryset based on the selected country."""
        if self.value():
            return queryset.filter(
                deal__boostrdealproduct__boostr_product__country=self.value()
            ).distinct()
        return queryset


@admin.register(CampaignOverview)
class CampaignOverviewAdmin(admin.ModelAdmin):
    """Admin model for sales products imported from Boostr. Deals are many-to-many with products"""

    model = CampaignOverview

    list_filter = [
        MonthFilter,
        CountryFilter,
        PlacementFilter,
        "deal__advertiser",
    ]

    readonly_fields: list[str] = [
        "net_ecpm",
    ]

    list_display = [
        "ad_ops_person",
        "notes",
        "kevel_flight_id",
        "net_spend",
        "impressions_sold",
        "net_ecpm",
        "seller",
        "deal",
    ]


@admin.register(CampaignOverviewSummary)
class CampaignSummaryAdmin(admin.ModelAdmin):
    """Admin model for sales products imported from Boostr. Deals are many-to-many with products"""

    change_list_template = "admin/campaign_summary.html"

    model = CampaignOverviewSummary

    list_filter = [MonthFilter, CountryFilter, PlacementFilter, "deal__advertiser"]

    def changelist_view(self, request, extra_context=None):
        """Customize the changelist view to include aggregated data based on filters."""
        print("change list veow is called ....")
        extra_context = extra_context or {}

        # Get the selected month filter value
        month_filter_value = request.GET.get("month", None)
        country_filter_value = request.GET.get("country", None)
        placement_filter_value = request.GET.get("placement", None)
        deal__advertiser_value = request.GET.get("deal__advertiser", None)

        print("month_filter_value", month_filter_value)

        # Apply the filter to the queryset and perform aggregation
        aggregated_query = BoostrDeal.objects.filter(
            campaignoverview__impressions_sold__isnull=False
        ).distinct()

        if month_filter_value:
            aggregated_query = aggregated_query.filter(
                boostrdealproduct__month=month_filter_value
            )

        if country_filter_value:
            country_subquery = BoostrProduct.objects.filter(
                boostrdealproduct__boostr_deal=OuterRef("pk"),
                country=country_filter_value,
            ).values("boostrdealproduct__boostr_deal")[:1]
            aggregated_query = aggregated_query.filter(
                pk__in=Subquery(country_subquery)
            )

        if placement_filter_value:
            placement_subquery = BoostrProduct.objects.filter(
                boostrdealproduct__boostr_deal=OuterRef("pk"),
                full_name=placement_filter_value,
            ).values("boostrdealproduct__boostr_deal")[:1]
            aggregated_query = aggregated_query.filter(
                pk__in=Subquery(placement_subquery)
            )

        if deal__advertiser_value:
            aggregated_query = aggregated_query.filter(
                advertiser=deal__advertiser_value
            )

        latest_notes_subquery = (
            CampaignOverview.objects.filter(deal=OuterRef("pk"))
            .order_by("-updated_on")
            .values("notes")[:1]
        )

        latest_seller_subquery = (
            CampaignOverview.objects.filter(deal=OuterRef("pk"))
            .order_by("-updated_on")
            .values("seller")[:1]
        )

        latest_ad_ops_subquery = (
            CampaignOverview.objects.filter(deal=OuterRef("pk"))
            .order_by("-updated_on")
            .values("ad_ops_person")[:1]
        )

        aggregated_data = (
            aggregated_query.values("advertiser")  # Group by advertiser
            .annotate(
                total_impressions_sold=Sum(
                    "campaignoverview__impressions_sold", output_field=FloatField()
                ),
                total_net_spend=Sum(
                    "campaignoverview__net_spend", output_field=FloatField()
                ),
                latest_note=Subquery(latest_notes_subquery),
                latest_seller=Subquery(latest_seller_subquery),
                latest_ad_ops=Subquery(latest_ad_ops_subquery),
            )
            .values(
                "advertiser",
                "total_impressions_sold",
                "total_net_spend",
                "latest_note",
                "latest_seller",
                "latest_ad_ops",
            )
        )

        # Calculate total_net_ecpm in Python
        for item in aggregated_data:
            if item["total_impressions_sold"] > 0:
                item["total_net_ecpm"] = (
                    item["total_net_spend"] / item["total_impressions_sold"]
                ) * 1000
            else:
                item["total_net_ecpm"] = 0  # Or None, based on your preference

        response = super().changelist_view(request, extra_context=extra_context)
        response.context_data["summary"] = list(aggregated_data)

        return response
