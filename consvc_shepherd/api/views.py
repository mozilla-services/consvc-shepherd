from consvc_shepherd.models import BoostrProduct
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from consvc_shepherd.models import BoostrProduct
from consvc_shepherd.api.serializers import BoostrProductSerializer

@api_view(['GET'])
def get_products(request):
    products = BoostrProduct.objects.all()
    serializer = BoostrProductSerializer(products, many=True)
    return Response(serializer.data)
