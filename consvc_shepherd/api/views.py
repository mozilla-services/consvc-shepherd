"""Dashboard API views that produce json data"""

from rest_framework.permissions import AllowAny
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
    permission_classes = [AllowAny]  # This allows unauthenticated access


class CampaignViewSet(ModelViewSet):
    """Fetch all Campaigns"""

    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [AllowAny]  # This allows unauthenticated access


class BoostrDealViewSet(ModelViewSet):
    """Fetch all BoostrDeal"""

    queryset = BoostrDeal.objects.all()
    serializer_class = BoostrDealSerializer
    permission_classes = [AllowAny]  # This allows unauthenticated access
