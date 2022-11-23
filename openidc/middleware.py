from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.http import HttpResponse


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
        default_email = settings.DEV_USER_EMAIL if settings.DEBUG else None
        openidc_header_value = request.META.get(settings.OPENIDC_HEADER, default_email)

        if openidc_header_value is None:
            # If a user has bypassed the OpenIDC flow entirely and no header
            # is set then we reject the request entirely
            return HttpResponse("Please login using OpenID Connect", status=401)

        try:
            openidc_email = openidc_header_value.split(settings.OPENIDC_HEADER_PREFIX)[
                -1
            ]
            user = self.User.objects.get(username=openidc_email)
        except self.User.DoesNotExist:
            user = self.User(username=openidc_email, email=openidc_email)
            if user.email == settings.DEV_USER_EMAIL and settings.DEBUG:
                user.is_superuser = True
                user.is_staff = True
            user.save()

        request.user = user

        return self.get_response(request)
