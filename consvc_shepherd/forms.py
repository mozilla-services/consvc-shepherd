"""Forms module for consvc_shepherd."""
import json
from typing import Any, Dict

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.forms.models import inlineformset_factory
from django.utils import dateformat, timezone
from jsonschema import exceptions, validate

from consvc_shepherd.models import (
    AllocationSetting,
    AllocationSettingsSnapshot,
    PartnerAllocation,
    SettingsSnapshot,
)
from consvc_shepherd.utils import ShepherdMetrics
from contile.models import Partner

metrics: ShepherdMetrics = ShepherdMetrics("shepherd")


class SnapshotCompareForm(forms.Form):
    """Form model comparing Partner snapshots.

    Attributes
    ----------
    older_snapshot : ModelChoiceField
        Old snapshot value selector
    newer_snapshot : ModelChoiceField
        New snapshot value selector

    Methods
    -------
    compare(self)
        Compare older_snapshot to newer_snapshot advertiser data.
        Compares json settings for each object and returns a dictionary
        capturing added and removed advertiser.
    """

    older_snapshot = forms.ModelChoiceField(
        label="Older Snapshot",
        queryset=SettingsSnapshot.objects.all().order_by("-created_on"),
    )
    newer_snapshot = forms.ModelChoiceField(
        label="Newer Snapshot",
        queryset=SettingsSnapshot.objects.all().order_by("-created_on"),
    )

    def compare(self) -> dict[str, Any]:
        """Compare older_snapshot to newer_snapshot advertiser data."""
        os = SettingsSnapshot.objects.get(id=self.data["older_snapshot"])
        ns = SettingsSnapshot.objects.get(id=self.data["newer_snapshot"])
        older_json_settings = os.json_settings
        newer_json_settings = ns.json_settings

        older_advertisers = set(older_json_settings["adm_advertisers"].keys())
        newer_advertisers = set(newer_json_settings["adm_advertisers"].keys())

        added_advertisers = sorted(newer_advertisers - older_advertisers)
        removed_advertisers = sorted(older_advertisers - newer_advertisers)
        return {
            "title": f"Comparing {os.name} with {ns.name}",
            "differences": [
                {"diff_type": "Added Advertisers", "diff_value": added_advertisers},
                {"diff_type": "Removed Advertisers", "diff_value": removed_advertisers},
            ],
        }


class AllocationSettingsSnapshotForm(forms.ModelForm):
    """Form for AllocationSettings Snapshot Model for the UI.

    Attributes
    ----------
    name : CharField
        name of the snapshot

    Methods
    -------
    clean(self)
        additional validation to validate json generated
    get_json_settings(self)
        generate JSON based on allocation settings
    """

    name = forms.CharField(max_length=128)

    class Meta:
        """Meta Class."""

        model = AllocationSettingsSnapshot
        fields = "__all__"

    def clean(self):
        """Validate json generated."""
        cd = super(AllocationSettingsSnapshotForm, self).clean()
        cd["json_settings"] = self.get_json_settings()
        with open("./schema/allocation.schema.json", "r") as f:
            settings_schema = json.load(f)
            try:
                validate(cd["json_settings"], schema=settings_schema)
                metrics.incr("allocation.snapshot.schema.validation.success")
            except exceptions.ValidationError as e:
                metrics.incr("allocation.snapshot.schema.validation.fail")
                raise ValidationError(
                    message=f"JSON generated is different from the expected allocation schema. "
                    f"Ensure that there are two allocation settings: {e}",
                )
        return cd

    def get_json_settings(self) -> Dict[str, Any]:
        """Generate JSON based on allocation settings."""
        allocation_settings_name: str = (
            f"SOV-{dateformat.format(timezone.now(), 'YmdHis')}"
        )
        return {
            "name": allocation_settings_name,
            "allocations": [
                allocation.to_dict()
                for allocation in AllocationSetting.objects.all().order_by("position")
            ],
        }


class PartnerAllocationForm(forms.ModelForm):
    """Partner Specific Allocation Class Form."""

    partner = forms.ModelChoiceField(
        queryset=Partner.objects.all(),
        widget=forms.Select(attrs={"class": "form-select mx-2"}),
    )
    percentage = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={"class": "form-control mx-2"}),
    )

    class Meta:
        """Meta class for PartnerAllocationForm."""

        model = PartnerAllocation
        fields = "__all__"


class AllocationSettingForm(forms.ModelForm):
    """Allocation Settings Class Form.

    Attributes
    ----------
    position : IntegerField
        1-based position form value.
    """

    position = forms.IntegerField(
        min_value=1,
        max_value=settings.CONTILE_MAX_TILES,
        help_text="Position value is 1-based",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    class Meta:
        """Meta class for AllocationSettingForm."""

        model = AllocationSetting
        fields = "__all__"


class AllocationSettingFormset(BaseInlineFormSet):
    """Allocation Settings Class Formset."""

    def clean(self):
        """Additional Form Validation."""
        super(AllocationSettingFormset, self).clean()
        alive_forms = [
            form for form in self.forms if not form.cleaned_data.get("DELETE")
        ]

        if alive_forms:
            if (
                min((form.cleaned_data.get("percentage", 0) for form in alive_forms))
                <= 0
            ):
                raise forms.ValidationError(
                    "Allocation percentage must be greater than 0."
                )

        if sum((form.cleaned_data.get("percentage", 0) for form in alive_forms)) != 100:
            raise forms.ValidationError("Total Percentage has to add up to 100.")

        partners = [form.cleaned_data.get("partner", "") for form in alive_forms]

        if len(set(partners)) < len(partners):
            raise forms.ValidationError("A Partner is listed multiple times.")


AllocationFormset = inlineformset_factory(
    AllocationSetting,
    PartnerAllocation,
    form=PartnerAllocationForm,
    formset=AllocationSettingFormset,
    extra=1,
    can_delete=True,
    can_delete_extra=True,
)
