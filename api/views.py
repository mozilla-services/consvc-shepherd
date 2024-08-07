""" from rest_framework import permissions, viewsets
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from consvc_shepherd.models import BoostrProduct
from .serializers import BoostrProductSerializer


@method_decorator(csrf_exempt, name='dispatch')
class BoostrProductViewSet(viewsets.ModelViewSet):
    queryset = BoostrProduct.objects.all()
    serializer_class = BoostrProductSerializer
    permission_class = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'boostr_id'

    def get_object(self):
        boostr_id = self.kwargs.get("boostr_id")
        obj = get_object_or_404(BoostrProduct, boostr_id=boostr_id)
        self.check_object_permissions(self.request,obj)
        return obj """