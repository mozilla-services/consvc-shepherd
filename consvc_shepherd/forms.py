"""Forms module for consvc_shepherd."""
from typing import Any

from django import forms
from django.forms import BaseInlineFormSet
from django.forms.models import inlineformset_factory

from consvc_shepherd.models import (
    AllocationSetting,
    PartnerAllocation,
    SettingsSnapshot,
)
from contile.models import Partner


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


class PartnerAllocationForm(forms.ModelForm):
    """Partner Specific Allocation Class Form."""

    partner = forms.ModelChoiceField(queryset=Partner.objects.all())
    percentage = forms.IntegerField(min_value=0, max_value=100)

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

    position = forms.IntegerField(min_value=1, help_text="Position value is 1-based")

    class Meta:
        """Meta class for AllocationSettingForm."""

        model = AllocationSetting
        fields = "__all__"


class AllocationSettingFormset(BaseInlineFormSet):
    """Allocation Settings Class Formset."""

    def clean(self):
        """Additional Form Validation."""
        super(AllocationSettingFormset, self).clean()

        if sum((form.cleaned_data.get("percentage") for form in self.forms)) != 100:
            raise forms.ValidationError("Total Percentage has to add up to 100.")

        partners = [form.cleaned_data.get("partner").name for form in self.forms]

        if len(set(partners)) < len(partners):
            raise forms.ValidationError("A Partner is listed multiple times.")


AllocationFormset = inlineformset_factory(
    AllocationSetting,
    PartnerAllocation,
    form=PartnerAllocationForm,
    formset=AllocationSettingFormset,
    extra=1,
    can_delete=False,
    can_delete_extra=True,
)
