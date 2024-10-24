"""aconsvc_shepherd API URL Configuration

This module defines the URL patterns for the API endpoints of the consvc_shepherd application,
specifically for the dashboard app views. It uses Django REST Framework's router to automatically
generate the URL patterns for the API views.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BoostrDealViewSet,
    CampaignSummaryViewSet,
    CampaignViewSet,
    ProductViewSet,
)

router = DefaultRouter()
router.register(r"deals", BoostrDealViewSet, basename="deals")
router.register(r"campaigns", CampaignViewSet, basename="campaigns")
router.register(r"products", ProductViewSet, basename="products")
router.register(r"campaign/overview", CampaignSummaryViewSet, basename="overview")

urlpatterns = [
    path("", include(router.urls)),
]
