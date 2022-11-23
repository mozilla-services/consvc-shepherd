import mock
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings


from openidc.middleware import OpenIDCAuthMiddleware


class OpenIDCAuthMiddlewareTests(TestCase):
    def setUp(self):
        self.response = "Response"
        self.middleware = OpenIDCAuthMiddleware(lambda request: self.response)

        mock_resolve_patcher = mock.patch("django.urls.resolve")
        self.mock_resolve = mock_resolve_patcher.start()
        self.addCleanup(mock_resolve_patcher.stop)

    @override_settings(OPENIDC_EMAIL_HEADER_PREFIX="accounts.google.com:")
    def test_user_created_with_correct_email_from_header(self):
        header_value = "accounts.google.com:user@example.com"

        request = mock.Mock()
        request.META = {settings.OPENIDC_EMAIL_HEADER: header_value}

        User = get_user_model()
        self.assertEqual(User.objects.all().count(), 0)

        response = self.middleware(request)

        self.assertEqual(response, self.response)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual("user@example.com", request.user.email)

    @override_settings(OPENIDC_EMAIL_HEADER_PREFIX=None)
    def test_user_created_with_dev_email_when_no_header(self):
        header_value = "user@example.com"

        request = mock.Mock()
        request.META = {settings.OPENIDC_EMAIL_HEADER: header_value}

        User = get_user_model()

        self.assertEqual(User.objects.all().count(), 0)
        response = self.middleware(request)

        self.assertEqual(response, self.response)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual("user@example.com", request.user.email)
