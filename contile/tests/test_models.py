from django.core.exceptions import ValidationError
from django.test import TestCase

from contile.models import Advertiser, AdvertiserUrl, Partner


class TestPartnerModel(TestCase):
    def test_to_dict_produces_correctly(self):
        partner = Partner.objects.create(
            name="Partner Advertiser",
        )
        advertiser1 = Advertiser.objects.create(name="Pocket", partner=partner)
        advertiser2 = Advertiser.objects.create(name="Firefox", partner=partner)
        AdvertiserUrl.objects.create(
            advertiser=advertiser1,
            path="/hello/",
            matching=False,
            domain="example.com",
            geo="CA",
        )
        AdvertiserUrl.objects.create(
            advertiser=advertiser1,
            path="/",
            matching=True,
            domain="example.com",
            geo="CA",
        )
        AdvertiserUrl.objects.create(
            advertiser=advertiser1,
            path="/read/",
            matching=False,
            domain="1.example.com",
            geo="CA",
        )
        AdvertiserUrl.objects.create(
            advertiser=advertiser1,
            path="/read/",
            matching=False,
            domain="example.com",
            geo="DE",
        )
        AdvertiserUrl.objects.create(
            advertiser=advertiser2,
            path="/read/",
            matching=False,
            domain="example.com",
            geo="DE",
        )
        self.maxDiff = None
        expected_result = {
            "adm_advertisers": {
                "Firefox": {
                    "DE": [
                        {
                            "host": "example.com",
                            "paths": [{"matching": "prefix", "value": "/read/"}],
                        }
                    ]
                },
                "Pocket": {
                    "CA": [
                        {
                            "host": "1.example.com",
                            "paths": [{"matching": "prefix", "value": "/read/"}],
                        },
                        {
                            "host": "example.com",
                            "paths": [
                                {"matching": "exact", "value": "/"},
                                {"matching": "prefix", "value": "/hello/"},
                            ],
                        },
                    ],
                    "DE": [
                        {
                            "host": "example.com",
                            "paths": [{"matching": "prefix", "value": "/read/"}],
                        }
                    ],
                },
            }
        }

        self.assertEqual(partner.to_dict(), expected_result)


class TestAdvertiserUrlModel(TestCase):
    def setUp(self):
        self.partner = Partner.objects.create(name="Partner Advertiser")
        self.advertiser = Advertiser.objects.create(
            name="Advertiser Name", partner=self.partner
        )

    def test_ad_url_invalid_domain_structure(self):
        with self.assertRaises(ValidationError) as e:
            AdvertiserUrl.objects.create(
                geo="CA",
                domain="example.",
                path="/hello/",
                matching=False,
                advertiser=self.advertiser,
            )
        self.assertIn(
            "hostnames should have the structure <leaf-domain>.<second-level-domain>.<top-domain> or <second-level-domain>.<top-domain>",
            str(e.exception),
        )

    def test_ad_url_invalid_domain_structure_double_dots(self):
        with self.assertRaises(ValidationError) as e:
            AdvertiserUrl.objects.create(
                geo="CA",
                domain="example..com",
                path="/hello/",
                matching=False,
                advertiser=self.advertiser,
            )
        self.assertIn(
            "hostnames should have the structure <leaf-domain>.<second-level-domain>.<top-domain> or <second-level-domain>.<top-domain>",
            str(e.exception),
        )

    def test_ad_url_invalid_prefix_value_with_singular_slash(self):
        with self.assertRaises(ValidationError) as e:
            AdvertiserUrl.objects.create(
                geo="CA",
                domain="example.com",
                path="/",
                matching=False,
                advertiser=self.advertiser,
            )
        self.assertIn(
            "Prefix paths can't be just '/'",
            str(e.exception),
        )

    def test_ad_url_invalid_prefix_without_ending_slash(self):
        with self.assertRaises(ValidationError) as e:
            AdvertiserUrl.objects.create(
                geo="CA",
                domain="example.com",
                path="/hello",
                matching=False,
                advertiser=self.advertiser,
            )
        self.assertIn(
            "All paths need to start and end with '/'",
            str(e.exception),
        )

    def test_ad_url_with_valid_prefix_saves_correctly(self):
        AdvertiserUrl.objects.create(
            geo="FR",
            domain="example.com",
            path="/prefix/",
            matching=False,
            advertiser=self.advertiser,
        )
        self.assertEqual(
            AdvertiserUrl.objects.filter(
                geo="FR",
                domain="example.com",
                path="/prefix/",
                matching=False,
                advertiser=self.advertiser,
            ).count(),
            1,
        )

    def test_ad_url_with_valid_exact_saves_correctly(self):
        AdvertiserUrl.objects.create(
            geo="BR",
            domain="example.com",
            path="/exact/",
            matching=True,
            advertiser=self.advertiser,
        )
        self.assertEqual(
            AdvertiserUrl.objects.filter(
                geo="BR",
                domain="example.com",
                path="/exact/",
                matching=True,
                advertiser=self.advertiser,
            ).count(),
            1,
        )

    def test_ad_url_with_valid_leaf_domain_saves_correctly(self):
        AdvertiserUrl.objects.create(
            geo="BR",
            domain="www.example.com",
            path="/exact/",
            matching=True,
            advertiser=self.advertiser,
        )
        self.assertEqual(
            AdvertiserUrl.objects.filter(
                geo="BR",
                domain="www.example.com",
                path="/exact/",
                matching=True,
                advertiser=self.advertiser,
            ).count(),
            1,
        )
