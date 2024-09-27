"""Dashboard API views that produce json data"""

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from consvc_shepherd.api.serializers import (
    BoostrDealSerializer,
    BoostrProductSerializer,
    CampaignSerializer,
)
from consvc_shepherd.models import BoostrDeal, BoostrProduct, Campaign


class ProductViewSet(ReadOnlyModelViewSet):
    """Fetch all BoostrProducts"""

    queryset = BoostrProduct.objects.all()
    serializer_class = BoostrProductSerializer


class CampaignViewSet(ModelViewSet):
    """Fetch all Campaigns"""

    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer


class BoostrDealViewSet(ReadOnlyModelViewSet):
    """Fetch all BoostrDeal"""

    queryset = BoostrDeal.objects.all()
    serializer_class = BoostrDealSerializer
