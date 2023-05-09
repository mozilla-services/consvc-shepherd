"""Tests related to the verification of OpenIDCAuthMiddleware."""
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

        mock_verify_token_patcher = mock.patch(
            "google.oauth2.id_token.verify_token")

        self.mock_verify_token = mock_verify_token_patcher.start()
        self.mock_verify_token.return_value = {"email": "non-dev@example.com"}
        self.addCleanup(mock_verify_token_patcher.stop)

    @override_settings(OPENIDC_HEADER_PREFIX="accounts.google.com:", DEBUG=True)
    def test_user_created_with_correct_email_from_header(self):
        header_value = "accounts.google.com:user@example.com"

        request = mock.Mock()
        request.META = {settings.OPENIDC_HEADER: header_value}

        User = get_user_model()
        self.assertEqual(User.objects.all().count(), 0)

        response = self.middleware(request)

        self.assertEqual(response, self.response)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual("user@example.com", request.user.email)

    @override_settings(DEBUG=True)
    def test_user_created_with_dev_email_when_no_header(self):

        request = mock.Mock()
        request.META = {}
        User = get_user_model()

        self.assertEqual(User.objects.all().count(), 0)
        response = self.middleware(request)

        self.assertEqual(response, self.response)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual("dev@example.com", request.user.email)

    @override_settings(DEBUG=False)
    def test_user_created_with_jwt_header(self):
        header_value = "x-goog-iap-jwt-assertion"

        request = mock.Mock()
        request.META = {settings.OPENIDC_HEADER: header_value}

        User = get_user_model()

        self.assertEqual(User.objects.all().count(), 0)
        response = self.middleware(request)

        self.assertEqual(response, self.response)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual("non-dev@example.com", request.user.email)
