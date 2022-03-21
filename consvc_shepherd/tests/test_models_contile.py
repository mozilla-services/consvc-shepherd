from django.core.exceptions import ValidationError
from django.test import TestCase

from consvc_shepherd.models import Partner, Advertiser, AdvertiserUrl


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

    def test_to_dict_produces_correctly(self):
        partner = Partner.objects.create(
            name="Partner Advertiser",
            impression_hosts=["example.com", "1.example.com"],
            click_hosts=["2.example.com"],
        )
        advertiser1 = Advertiser.objects.create(name="Pocket", partner=partner)
        advertiser2 = Advertiser.objects.create(name="Firefox", partner=partner)
        AdvertiserUrl.objects.create(
            advertiser=advertiser1,
            path="/",
            matching=False,
            domain="example.com",
            geo="Canada",
        )
        AdvertiserUrl.objects.create(
            advertiser=advertiser1,
            path="/hello",
            matching=False,
            domain="example.com",
            geo="Canada",
        )
        AdvertiserUrl.objects.create(
            advertiser=advertiser1,
            path="/read",
            matching=True,
            domain="1.example.com",
            geo="Canada",
        )
        AdvertiserUrl.objects.create(
            advertiser=advertiser1,
            path="/read",
            matching=False,
            domain="example.com",
            geo="Germany",
        )
        AdvertiserUrl.objects.create(
            advertiser=advertiser2,
            path="/read",
            matching=False,
            domain="example.com",
            geo="Germany",
        )
        self.maxDiff = None
        expected_result = {
            "DEFAULT": {
                "click_hosts": ["2.example.com"],
                "impression_hosts": ["example.com", "1.example.com"],
            },
            "Firefox": {
                "DE": [
                    {
                        "host": "example.com",
                        "paths": [{"matching": "prefix", "value": "/read"}],
                    }
                ]
            },
            "Pocket": {
                "CA": [
                    {
                        "host": "1.example.com",
                        "paths": [{"matching": "exact", "value": "/read"}],
                    },
                    {
                        "host": "example.com",
                        "paths": [
                            {"matching": "prefix", "value": "/"},
                            {"matching": "prefix", "value": "/hello"},
                        ],
                    },
                ],
                "DE": [
                    {
                        "host": "example.com",
                        "paths": [{"matching": "prefix", "value": "/read"}],
                    }
                ],
            },
        }

        self.assertEqual(partner.to_dict(), expected_result)
