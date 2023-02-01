from django import forms

from consvc_shepherd.models import SettingsSnapshot


class SnapshotCompareForm(forms.Form):
    older_snapshot = forms.CharField(
        label="Older Snapshot",
        widget=forms.Select(
            choices=(
                (snapshot.name, snapshot)
                for snapshot in SettingsSnapshot.objects.all().order_by("-created_on")
            )
        ),
    )
    newer_snapshot = forms.CharField(
        label="Newer Snapshot",
        widget=forms.Select(
            choices=(
                (snapshot.name, snapshot)
                for snapshot in SettingsSnapshot.objects.all().order_by("-created_on")
            )
        ),
    )

    def compare(self):
        os_name = self.data["older_snapshot"]
        ns_name = self.data["newer_snapshot"]
        older_json_settings = SettingsSnapshot.objects.get(name=os_name).json_settings
        newer_json_settings = SettingsSnapshot.objects.get(name=ns_name).json_settings

        older_advertisers = set(older_json_settings["adm_advertisers"].keys())
        newer_advertisers = set(newer_json_settings["adm_advertisers"].keys())

        added_advertisers = sorted(newer_advertisers - older_advertisers)
        removed_advertisers = sorted(older_advertisers - newer_advertisers)
        return {
            "title": f"Comparing {os_name} with {ns_name}",
            "differences": [
                {"diff_type": "Added Advertisers", "diff_value": added_advertisers},
                {"diff_type": "Removed Advertisers", "diff_value": removed_advertisers},
            ],
        }
