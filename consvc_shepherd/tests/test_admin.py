from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase

from consvc_shepherd.admin import ModelAdmin
from consvc_shepherd.models import Partner, SettingsSnapshot
from consvc_shepherd.tests.factories import UserFactory


class MyAdminTest(TestCase):
    def setUp(self):
        request_factory = RequestFactory()
        self.request = request_factory.get("/admin")
        self.request.user = UserFactory()

        site = AdminSite()
        self.admin = ModelAdmin(SettingsSnapshot, site)
        self.partner = Partner.objects.create(name="Partner1")

    def test_get_read_only_fields_when_obj_exists(self):
        obj = SettingsSnapshot.objects.create(
            name="Snapshot", settings_type=self.partner
        )
        fields = self.admin.get_readonly_fields(self.request, obj)
        self.assertEqual(
            fields,
            [
                "name",
                "settings_type",
                "json_settings",
                "created_by",
                "launched_by",
                "launched_date",
            ],
        )

    def test_get_read_only_fields_when_obj_does_not_exists(self):
        fields = self.admin.get_readonly_fields(self.request, None)
        self.assertEqual(
            fields, ["json_settings", "created_by", "launched_by", "launched_date"]
        )

    def test_save_model_generates_json(self):
        self.assertEqual(SettingsSnapshot.objects.all().count(), 0)

        expected_json = self.partner.to_dict()
        self.admin.save_model(
            self.request, SettingsSnapshot(settings_type=self.partner), None, {}
        )

        self.assertEqual(SettingsSnapshot.objects.all().count(), 1)
        snapshot = SettingsSnapshot.objects.all().first()
        self.assertEqual(snapshot.json_settings, expected_json)
