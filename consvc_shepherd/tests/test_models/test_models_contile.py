from django.core.exceptions import ValidationError
from django.test import TestCase
from consvc_shepherd.models import Partner


class TestPartnerModel(TestCase):
    def test_hostname_for_invalid_impressions_hosts(self):
        with self.assertRaises(ValidationError):
            Partner.objects.create(
                name="Partner Advertiser",
                impression_hosts=["example.com", "ex@@@@m@@@ple.com"],
                click_hosts=["example.com"],
            )

    def test_hostname_for_invalid_click_hosts(self):
        with self.assertRaises(ValidationError):
            Partner.objects.create(
                name="Partner Advertiser",
                impression_hosts=["example.com", "test.example.com"],
                click_hosts=["example.com", "ex@&!mple.com"],
            )
