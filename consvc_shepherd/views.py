from typing import Any

from django.shortcuts import render
from django.views.generic import TemplateView

from consvc_shepherd.forms import SnapshotCompareForm
from consvc_shepherd.models import SettingsSnapshot


class TableOverview(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["data"] = SettingsSnapshot.objects.all().order_by("-created_on")
        context["form"] = SnapshotCompareForm
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = SnapshotCompareForm(request.POST)
        if form.is_valid():
            context["comparison_values"] = form.compare()
            return render(request, self.template_name, context=context)
        else:
            context["errors"] = form.errors
            return render(request, self.template_name, context=context)
