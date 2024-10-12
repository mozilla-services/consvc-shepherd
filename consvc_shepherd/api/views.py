"""Dashboard API views that produce json data"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from consvc_shepherd.api.serializers import (
    BoostrDealSerializer,
    BoostrProductSerializer,
    CampaignSerializer,
    InventorySerializer,
    SplitCampaignSerializer,
)
from consvc_shepherd.models import BoostrDeal, BoostrProduct, Campaign, Inventory


class ProductViewSet(ReadOnlyModelViewSet):
    """Fetch all BoostrProducts"""

    queryset = BoostrProduct.objects.all()
    serializer_class = BoostrProductSerializer


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


class InventoryViewSet(ReadOnlyModelViewSet):
    """Fetch all inventory overview data"""

    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
