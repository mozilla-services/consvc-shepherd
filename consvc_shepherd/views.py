"""Views module for consvc_shepherd."""
from typing import Any

from django.shortcuts import render
from django.views.generic import ListView, TemplateView

from consvc_shepherd.forms import SnapshotCompareForm
from consvc_shepherd.models import (
    AllocationSetting,
    AllocationSettingsSnapshot,
    SettingsSnapshot,
)


class TableOverview(TemplateView):
    """TableOverview TemplateView Class

    Attributes
    ----------
    template_name : str
        Directory and file for given TableOverview template

    Methods
    -------
    get_context_data(self, **kwargs: Any)
        Return ordered context data from all SettingsSnapshot instances.
    post(self, request, *args, **kwargs)
        Post data entered in SnapshotCompareForm.
    """

    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Return ordered context data from all SettingsSnapshot instances."""
        context = super().get_context_data(**kwargs)
        context["data"] = SettingsSnapshot.objects.all().order_by("-created_on")
        context["form"] = SnapshotCompareForm
        return context

    def post(self, request, *args, **kwargs):
        """Post data entered in SnapshotCompareForm."""
        context = self.get_context_data()
        form = SnapshotCompareForm(request.POST)
        if form.is_valid():
            context["comparison_values"] = form.compare()
            return render(request, self.template_name, context=context)
        else:
            context["errors"] = form.errors
            return render(request, self.template_name, context=context)


class AllocationSettingList(ListView):
    """AllocationSettingList ListView class.

    Attributes
    ----------
    model : AllocationSetting
        Specific AllocationSetting model
    template_name : str
        Directory and file for given AllocationSetting template

    Methods
    -------
    get_context_data(self, **kwargs: Any)
        Return ordered context data from all AllocationSetting instances.
    """

    model = AllocationSetting
    template_name = "allocation/allocation_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Return ordered context data from all AllocationSetting instances."""
        context = super().get_context_data(**kwargs)
        context["allocation_settings"] = AllocationSetting.objects.all().order_by(
            "position"
        )
        context["latest_snapshot"] = (
            AllocationSettingsSnapshot.objects.filter(launched_date__isnull=False)
            .order_by("-created_on")
            .first()
        )
        return context
