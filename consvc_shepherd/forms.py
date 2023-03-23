from django import forms

from consvc_shepherd.models import SettingsSnapshot


class SnapshotCompareForm(forms.Form):
    older_snapshot = forms.ModelChoiceField(
        label="Older Snapshot",
        queryset=SettingsSnapshot.objects.all().order_by("-created_on"),
    )
    newer_snapshot = forms.ModelChoiceField(
        label="Newer Snapshot",
        queryset=SettingsSnapshot.objects.all().order_by("-created_on"),
    )

    def compare(self):
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
