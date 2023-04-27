"""Schema validation and testing module."""
import json
from typing import Any
from unittest import TestCase

import pytest
from jsonschema import validate

from consvc_shepherd.models import AllocationSetting, PartnerAllocation
from contile.models import Advertiser, AdvertiserUrl, Partner


@pytest.mark.django_db
class JSONSchema(TestCase):

    def test_filter_schema(self):
        """Tests filter schema for adM."""

        with open("./schema/adm_filter.schema.json", "r") as f:
            settings_schema = json.load(f)
            partner = Partner.objects.create(
                name="Partner Advertiser",
            )
            advertiser1 = Advertiser.objects.create(name="Pocket", partner=partner)
            # we want to test that Advertiser names with special characters are valid
            advertiser2 = Advertiser.objects.create(name="F!-reΩ fox+", partner=partner)
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

@pytest.mark.django_db
class JSONSchema(TestCase):

    def test_allocation_schema(self):
        """Tests allocation schema for SOV."""
        # pass
        with open("./schema/allocation.schema.json", "r") as f:
            allocations_schema = json.load(f)
            allocations: dict[str, Any] = {}
            allocations.update({"name": "SOV-20230101140000",
                               "allocations": []})
            pass
            adm_partner = Partner.objects.create(
                name="adm"
            )
            kevel_partner = Partner.objects.create(
                name="kevel"
            )
            allocations["allocations"].append({
                "position": AllocationSetting.objects.create(position=0),
                "allocation": PartnerAllocation.objects.create(
                allocationPosition=AllocationSetting.objects.create(position=0),
                partner=adm_partner,
                percentage=100
            )})
            allocation1_kevel = PartnerAllocation.objects.create(
                allocationPosition=AllocationSetting.objects.create(position=1),
                partner=kevel_partner,
                percentage=0
            )
            allocation2_adm = PartnerAllocation.objects.create(
                allocationPosition=AllocationSetting.objects.create(position=2),
                partner=adm_partner,
                percentage=85
            )
            allocation2_kevel = PartnerAllocation.objects.create(
                allocationPosition=AllocationSetting.objects.create(position=3),
                partner=kevel_partner,
                percentage=15
            )



