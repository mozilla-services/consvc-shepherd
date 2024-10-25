"""Filters for the CampaignSummary model based on various criteria."""

from django.db.models import Subquery
from django_filters import rest_framework as filters

from consvc_shepherd.models import BoostrDealProduct, CampaignSummary


class CampaignSummaryFilter(filters.FilterSet):
    """Filter for CampaignSummary model based on various fields."""

    advertiser = filters.CharFilter(
        label="Advertiser", field_name="advertiser", lookup_expr="icontains"
    )
    month = filters.CharFilter(label="Month", method="filter_month")
    placement = filters.CharFilter(label="Placement", method="filter_placement")
    country = filters.CharFilter(label="Country", method="filter_country")

    class Meta:
        """Meta class to specify the model and fields for the filter."""

        model = CampaignSummary
        fields = ["advertiser", "month", "placement", "country"]

    def filter_month(self, queryset, name, value):
        """Filter queryset by month using BoostrDealProduct."""
        return queryset.filter(
            deal_id__in=Subquery(
                BoostrDealProduct.objects.filter(month=value).values("boostr_deal_id")
            )
        )

    def filter_placement(self, queryset, name, value):
        """Filter queryset by placement using BoostrDealProduct."""
        return queryset.filter(
            deal_id__in=Subquery(
                BoostrDealProduct.objects.filter(boostr_product__id=value).values(
                    "boostr_deal_id"
                )
            )
        )

    def filter_country(self, queryset, name, value):
        """Filter queryset by country using BoostrDealProduct."""
        return queryset.filter(
            deal_id__in=Subquery(
                BoostrDealProduct.objects.filter(boostr_product__country=value).values(
                    "boostr_deal_id"
                )
            )
        )
