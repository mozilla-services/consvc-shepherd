import mock
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase

from consvc_shepherd.tests.factories import UserFactory
from contile.admin import PartnerListAdmin, approve_partner_settings
from contile.models import Partner


class PartnerAdminTest(TestCase):
    def setUp(self):
        request_factory = RequestFactory()
        self.request = request_factory.get("/admin")
        self.request.user = UserFactory()

        site = AdminSite()
        self.admin = PartnerListAdmin(Partner, site)
        self.partner = Partner.objects.create(
            name="Partner1", last_updated_by=self.request.user
        )

    def test_approve_partner_settings(self):
        request = mock.Mock()
        request.user = UserFactory()
        self.assertFalse(self.partner.is_active)
        self.assertIsNone(self.partner.last_approved_by)
        approve_partner_settings(None, request, [self.partner])
        self.assertTrue(self.partner.is_active)
        self.assertIsNotNone(self.partner.last_approved_by)

    def test_partner_admin_save_model(self):
        request = mock.Mock()
        request.user = UserFactory()

        self.partner.is_active = True
        self.partner.is_updated_by = UserFactory()
        self.partner.is_approved_by = UserFactory()
        self.partner.save()
        self.admin.save_model(request, self.partner, None, {})
        self.assertFalse(self.partner.is_active)
        self.assertIsNone(self.partner.last_approved_by)
        self.assertEqual(self.partner.last_updated_by, request.user)

    def test_approval_fails_when_updater_and_approver_are_the_same(self):
        request = mock.Mock()
        request.user = UserFactory()

        self.partner.is_active = False
        self.partner.last_updated_by = request.user
        self.partner.last_approved_by = None
        self.partner.save()
        approve_partner_settings(None, request, [self.partner])
        self.assertFalse(self.partner.is_active)
        self.assertIsNone(self.partner.last_approved_by)
        self.assertEqual(self.partner.last_updated_by, request.user)
