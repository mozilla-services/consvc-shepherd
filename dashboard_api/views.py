from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from dashboard_api.models import TestModel
from dashboard_api.serializers import TestModelSerializer

@api_view(['GET'])
def get_test_models(request):
    languages = TestModel.objects.all()
    serializer = TestModelSerializer(languages, many=True)
    return Response(serializer.data)
