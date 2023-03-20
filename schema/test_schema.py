from unittest import TestCase

from jsonschema import validate
import json

from contile.models import Partner, Advertiser, AdvertiserUrl


class JSONSchema(TestCase):

    def test_schema(self):
        with open("shepherd.schema.json", "r") as f:
            settings_schema = json.load(f)
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

            validate(partner.to_dict(), settings_schema)

