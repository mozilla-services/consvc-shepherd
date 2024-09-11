"""Routes for the dashboard API"""

from django.urls import path

from . import views

urlpatterns = [
    path("products", views.get_products, name="get_products"),
]
