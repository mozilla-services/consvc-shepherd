"""Dashboard API views that produce json data"""

from rest_framework.decorators import api_view
from rest_framework.response import Response

from consvc_shepherd.api.serializers import BoostrProductSerializer
from consvc_shepherd.models import BoostrProduct


@api_view(["GET"])
def get_products(request):
    """Fetch all BoostrProducts"""
    products = BoostrProduct.objects.all()
    serializer = BoostrProductSerializer(products, many=True)
    return Response(serializer.data)
