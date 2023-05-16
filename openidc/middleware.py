"""OpenIDC authentication middleware module for the consvc_shepherd service."""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.http import HttpResponse
from google.auth.transport import requests
from google.oauth2 import id_token

logger = logging.getLogger("shepherd")


def validate_iap_jwt(request):
    iap_jwt = request.META.get(settings.OPENIDC_HEADER)
    try:
        decoded_jwt = id_token.verify_token(
            iap_jwt,
            requests.Request(),
            audience=settings.IAP_AUDIENCE,
            certs_url="https://www.gstatic.com/iap/verify/public_key",
        )
        return decoded_jwt["email"]
    except Exception as e:
        logger.error(f"IAP JWT validation error: {e}")


def validate_openidc_header(request):
    default_email = settings.DEV_USER_EMAIL
    openidc_header_value = request.META.get(
        settings.OPENIDC_HEADER, default_email)
    return openidc_header_value.split(settings.OPENIDC_HEADER_PREFIX)[-1]


class OpenIDCAuthMiddleware(AuthenticationMiddleware):
    """
    An authentication middleware that depends on a header being set in the
    request. This header will be populated by nginx configured to authenticate
    with OpenIDC.
    We will automatically create a user object and attach it to the
    shepherd group.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.User = get_user_model()

    def __call__(self, request):
        if settings.DEBUG:
            openidc_email = validate_openidc_header(request)
        else:
            openidc_email = validate_iap_jwt(request)

        if openidc_email is None:
            # If a user has bypassed the OpenIDC flow entirely and no header
            # is set then we reject the request entirely
            return HttpResponse("Please login using OpenID Connect", status=401)

        try:
            user = self.User.objects.get(username=openidc_email)
        except self.User.DoesNotExist:
            user = self.User(username=openidc_email, email=openidc_email)
            if user.email == settings.DEV_USER_EMAIL and settings.DEBUG:
                user.is_superuser = True
                user.is_staff = True
            user.save()

        request.user = user

        return self.get_response(request)
