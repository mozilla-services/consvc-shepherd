"""Schema validation and testing module for supported schemas."""
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
            advertiser1 = Advertiser.objects.create(
                name="Pocket", partner=partner)
            # we want to test that Advertiser names with special characters are valid
            advertiser2 = Advertiser.objects.create(
                name="F!-reΩ fox+", partner=partner)
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

    def test_allocation_schema(self):
        """Tests partner allocation schema for SOV (Share of Voice)."""
        with open("./schema/allocation.schema.json", "r") as f:
            allocations_schema = json.load(f)
            allocations: dict[str, Any] = {}
            allocations.update(
                {"name": "SOV-20230101140000", "allocations": []})
            adm_partner: Partner = Partner.objects.create(
                name="adm"
            )
            kevel_partner: Partner = Partner.objects.create(
                name="k3-v-3l"
            )
            position1_alloc: AllocationSetting = AllocationSetting.objects.create(
                position=1
            )
            PartnerAllocation.objects.create(
                allocation_position=position1_alloc,
                partner=adm_partner,
                percentage=85
            )
            PartnerAllocation.objects.create(
                allocation_position=position1_alloc,
                partner=kevel_partner,
                percentage=15
            )
            allocations["allocations"].append(position1_alloc.to_dict())
            validate(allocations, allocations_schema)

            position2_alloc: AllocationSetting = AllocationSetting.objects.create(
                position=2
            )
            PartnerAllocation.objects.create(
                allocation_position=position2_alloc,
                partner=adm_partner,
                percentage=50
            )
            PartnerAllocation.objects.create(
                allocation_position=position2_alloc,
                partner=kevel_partner,
                percentage=50
            )
            allocations["allocations"].append(position2_alloc.to_dict())
            validate(allocations, allocations_schema)
