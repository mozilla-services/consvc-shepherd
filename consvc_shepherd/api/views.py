"""Dashboard API views that produce json data"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from consvc_shepherd.api.serializers import (
    BoostrDealSerializer,
    BoostrProductSerializer,
    CampaignSerializer,
    CampaignSummarySerializer,
    SplitCampaignSerializer,
)
from consvc_shepherd.models import BoostrDeal, BoostrProduct, Campaign, CampaignSummary

from .filters import CampaignSummaryFilter


class ProductViewSet(ReadOnlyModelViewSet):
    """Fetch all BoostrProducts"""

    queryset = BoostrProduct.objects.all()
    serializer_class = BoostrProductSerializer

    @action(detail=False, methods=["get"], url_path="countries")
    def get_countries(self, request):
        """Return a list of countries with their codes and names."""
        countries = [
            {"value": country.value, "label": country.label}
            for country in BoostrProduct.Countries
        ]
        return Response(countries, status=status.HTTP_200_OK)


class CampaignSummaryViewSet(ReadOnlyModelViewSet):
    """Fetch all Campaign Summaries"""

    queryset = CampaignSummary.objects.all()
    serializer_class = CampaignSummarySerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = CampaignSummaryFilter
    search_fields = [
        "advertiser",
        "net_spend",
        "impressions_sold",
        "clicks_delivered",
        "impressions_delivered",
    ]

    def list(self, request, *args, **kwargs):
        """Return all campaign summaries."""
        filtered_summaries = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(filtered_summaries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CampaignViewSet(ModelViewSet):
    """Fetch all Campaigns"""

    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    @action(detail=False, methods=["post"], url_path="split")
    def split_campaigns(self, request):
        """Handle split creation and updates of Campaigns."""
        serializer = SplitCampaignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        campaigns = serializer.save()
        return Response(
            CampaignSerializer(campaigns, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class BoostrDealViewSet(ReadOnlyModelViewSet):
    """Fetch all BoostrDeal"""

    queryset = BoostrDeal.objects.all()
    serializer_class = BoostrDealSerializer

    @action(detail=False, methods=["get"], url_path="advertisers")
    def get_advertisers(self, request):
        """Return a list of unique advertisers in the deals table."""
        advertisers = BoostrDeal.objects.values_list("advertiser", flat=True).distinct()
        advertiser_list = [
            {"value": advertiser, "label": advertiser} for advertiser in advertisers
        ]
        return Response(advertiser_list, status=status.HTTP_200_OK)
