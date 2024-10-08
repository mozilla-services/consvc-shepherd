"""consvc_shepherd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from consvc_shepherd.models import AllocationSetting
from consvc_shepherd.preview import PreviewView
from consvc_shepherd.views import (
    AllocationCreateView,
    AllocationSettingList,
    AllocationUpdateView,
    TableOverview,
)

urlpatterns = [
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path(
        "allocation/",
        AllocationSettingList.as_view(model=AllocationSetting),
        name="list_allocation",
    ),
    path(
        "allocation/create/",
        AllocationCreateView.as_view(),
    ),
    path("allocation/<int:pk>/", AllocationUpdateView.as_view()),
    path("preview", PreviewView.as_view()),
    path("", TableOverview.as_view()),
    path("api/v1/", include("consvc_shepherd.api.urls")),
]

admin.site.site_title = "Shepherd"
admin.site.site_header = "Shepherd"
admin.site.index_title = "Advertiser Settings Manager"
admin.site.enable_nav_sidebar = True
