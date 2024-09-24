"""Dashboard API views that produce json data"""

from rest_framework.viewsets import ModelViewSet

from consvc_shepherd.api.serializers import (
    BoostrDealSerializer,
    BoostrProductSerializer,
    CampaignSerializer,
)
from consvc_shepherd.models import BoostrDeal, BoostrProduct, Campaign


class ProductViewSet(ModelViewSet):
    """Fetch all BoostrProducts"""

    queryset = BoostrProduct.objects.all()
    serializer_class = BoostrProductSerializer


class CampaignViewSet(ModelViewSet):
    """Fetch all Campaigns"""

    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer


class BoostrDealViewSet(ModelViewSet):
    """Fetch all BoostrDeal"""

    queryset = BoostrDeal.objects.all()
    serializer_class = BoostrDealSerializer
