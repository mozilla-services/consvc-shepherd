from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from api import views
#from api.views import BoostrProductListViewSet

router = DefaultRouter()
router.include_format_suffixes = False
router.register(r'boostr_products',views.BoostrProductViewSet)

urlpatterns = [
    path("api/",include(router.urls)),
]   

urlpatterns = format_suffix_patterns(urlpatterns)