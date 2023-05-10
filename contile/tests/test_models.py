"""Tests related to the verification of Contile models.

Models:
- Advertiser
- AdvertiserUrl
- Partner
"""
from django.core.exceptions import ValidationError
from django.test import TestCase

from contile.models import Advertiser, AdvertiserUrl, Partner


class TestPartnerModel(TestCase):
    """Test class for Contile Partner Model. Extends Django TestCase.

    Methods
    -------
    test_to_dict_produces_correctly(self)
        Verifies a dictionary object is created from Partner model.

    """

    def test_to_dict_produces_correctly(self):
        """Verifies a dictionary object is created from Partner model."""
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
    """Test class for Contile AdvertiserUrl Model. Extends Django TestCase.

    Methods
    -------
    setUp(self)
        Create Partner and Advertiser objects.
    test_ad_url_invalid_domain_structure(self)
        Ensure invalid URL domain structure raises a ValidationError.
    test_ad_url_invalid_domain_structure_double_dots(self)
        Verify that invalid ad url that contains double dots raises a ValidationError.
    test_ad_url_invalid_prefix_value_with_singular_slash(self)
        Verify that ad url prefix consisting of single forward slash raises a ValidationError.
    test_ad_url_invalid_prefix_without_ending_slash(self)
        Verify that ad url without ending slash raises a ValidationError.
    test_ad_url_with_valid_prefix_saves_correctly(self)
        Verify that ad url with valid prefix saves as expected.
    test_ad_url_with_valid_exact_saves_correctly(self)
        Verify that exact matching ad url with saves as expected.
    test_ad_url_with_valid_leaf_domain_saves_correctly(self)
        Verify that ad url with validated leaf domain saves as expected.
    """

    def setUp(self):
        """Create Partner and Advertiser objects."""
        self.partner = Partner.objects.create(name="Partner Advertiser")
        self.advertiser = Advertiser.objects.create(
            name="Advertiser Name", partner=self.partner
        )

    def test_ad_url_invalid_domain_structure(self):
        """Ensure invalid URL domain structure raises a ValidationError.

        is_valid_host() function in models.py validates and raises said exception.
        """
        with self.assertRaises(ValidationError) as e:
            AdvertiserUrl.objects.create(
                geo="CA",
                domain="example.",
                path="/hello/",
                matching=False,
                advertiser=self.advertiser,
            )
        self.assertIn(
            "hostnames should have the structure <leaf-domain>.<second-level-domain>.<top-domain(s)>",
            str(e.exception),
        )

    def test_ad_url_invalid_domain_structure_double_dots(self):
        """Verify that invalid ad url that contains double dots raises a ValidationError."""
        with self.assertRaises(ValidationError) as e:
            AdvertiserUrl.objects.create(
                geo="CA",
                domain="www.example.co.uk.com",
                path="/hello/",
                matching=False,
                advertiser=self.advertiser,
            )
        self.assertIn(
            "hostnames should have the structure <leaf-domain>.<second-level-domain>.<top-domain(s)>",
            str(e.exception),
        )

    def test_ad_url_invalid_prefix_value_with_singular_slash(self):
        """Verify that ad url prefix consisting of single forward slash raises a ValidationError."""
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
        """Verify that ad url without ending slash raises a ValidationError."""
        with self.assertRaises(ValidationError) as e:
            AdvertiserUrl.objects.create(
                geo="CA",
                domain="example.com",
                path="/hello",
                matching=False,
                advertiser=self.advertiser,
            )
        self.assertIn(
            "Prefix paths can't be just '/' but needs to end with '/'",
            str(e.exception),
        )

    def test_ad_url_with_valid_prefix_saves_correctly(self):
        """Verify that ad url with valid prefix saves as expected."""
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
        """Verify that exact matching ad url with saves as expected."""
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
        """Verify that ad url with validated leaf domain saves as expected."""
        AdvertiserUrl.objects.create(
            geo="BR",
            domain="www.example.com",
            path="/exact",
            matching=True,
            advertiser=self.advertiser,
        )
        self.assertEqual(
            AdvertiserUrl.objects.filter(
                geo="BR",
                domain="www.example.com",
                path="/exact",
                matching=True,
                advertiser=self.advertiser,
            ).count(),
            1,
        )
