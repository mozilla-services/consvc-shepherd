from django.urls import path
from . import views


urlpatterns = [
    path('test_models/', views.get_test_models, name='get_test_models'),
]
