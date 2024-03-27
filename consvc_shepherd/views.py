"""Views module for consvc_shepherd."""

import json
from typing import Any

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from consvc_shepherd import settings
from consvc_shepherd.forms import (
    AllocationFormset,
    AllocationSettingForm,
    AllocationSettingsSnapshotForm,
    SnapshotCompareForm,
)
from consvc_shepherd.models import (
    AllocationSetting,
    AllocationSettingsSnapshot,
    SettingsSnapshot,
)
from consvc_shepherd.storage import send_to_storage
from consvc_shepherd.utils import ShepherdMetrics

metrics: ShepherdMetrics = ShepherdMetrics("shepherd")


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
        context["form"] = AllocationSettingsSnapshotForm
        return context

    def post(self, request, *args, **kwargs):
        """Post for allocationSettingsSnapshotForm."""
        self.object_list = AllocationSetting.objects.all()
        context = self.get_context_data(**kwargs)
        form = AllocationSettingsSnapshotForm(request.POST)

        if not form.is_valid():
            context["errors"] = form.errors
        else:
            instance = form.save(commit=False)
            instance.launched_by = self.request.user
            instance.created_by = self.request.user
            instance.launched_date = timezone.now()
            instance.json_settings = form.get_json_settings()
            instance.save()

            send_to_storage(
                json.dumps(instance.json_settings, indent=2),
                settings.ALLOCATION_FILE_NAME,
            )
            metrics.incr("allocation.upload.success")
            context["latest_snapshot"] = instance
        return render(request, self.template_name, context=context)


class AllocationViewMixin:
    """AllocationViewMixin Class.

    Methods
    -------
    form_valid(self, form)
        validates form data and saves accordingly
    """

    def form_valid(self, form):
        """Validate form data and saves models accordingly."""
        alloc_formset = self.get_context_data()["formset"]
        if not alloc_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form))
        variants = alloc_formset.save(commit=False)
        allocation_setting = form.save()
        for obj in alloc_formset.deleted_objects:
            obj.delete()
        for variant in variants:
            variant.allocation_position = allocation_setting
            variant.save()

        return HttpResponseRedirect("/allocation/")


class AllocationCreateView(AllocationViewMixin, CreateView):
    """AllocationSetting CreateView class.

    Attributes
    ----------
    model : AllocationSetting
        Specific AllocationSetting model
    url: str
        Url that view redirects to upon successful request
    form_class: AllocationSettingForm
        Form used for the view
    template_name : str
        Directory and file for given AllocationSetting template

    Methods
    -------
    get_context_data(self, **kwargs: Any)
        Return relevant form data for view.
    """

    model = AllocationSetting
    success_url = "/allocation/"
    form_class = AllocationSettingForm
    template_name = "allocation/allocation_create_or_edit.html"

    def get_context_data(self, **kwargs):
        """Get form data for view."""
        context = super(AllocationCreateView, self).get_context_data(**kwargs)
        if self.request.method == "GET":
            context["formset"] = AllocationFormset()
        else:
            context["formset"] = AllocationFormset(self.request.POST)
        return context


class AllocationUpdateView(AllocationViewMixin, UpdateView):
    """AllocationSettingList UpdateView class.

    Attributes
    ----------
    model : AllocationSetting
        Specific AllocationSetting model
    url: str
        Url that view redirects to upon successful request
    form_class: AllocationSettingForm
        Form used for the view
    template_name : str
        Directory and file for given AllocationSetting template

    Methods
    -------
    get_context_data(self, **kwargs: Any)
        Return relevant form data for view.
    """

    model = AllocationSetting
    success_url = "/allocation/"
    form_class = AllocationSettingForm
    template_name = "allocation/allocation_create_or_edit.html"

    def get_context_data(self, **kwargs):
        """Get form data for view."""
        context = super(AllocationUpdateView, self).get_context_data(**kwargs)
        if self.request.method == "POST":
            context["formset"] = AllocationFormset(
                self.request.POST or None, self.request.FILES, instance=self.object
            )
        else:
            context["formset"] = AllocationFormset(instance=self.object)
        return context
