"""Schema validation and testing module for supported schemas."""

import json
from typing import Any
from unittest import TestCase

import pytest
from jsonschema import exceptions, validate

from consvc_shepherd.models import AllocationSetting, PartnerAllocation
from contile.models import Advertiser, AdvertiserUrl, Partner


@pytest.mark.django_db
class TestJSONSchema(TestCase):
    """Test JSON schemas that Shepherd produces."""

    def setUp(self) -> None:
        """Set up test data"""
        self.amp_partner: Partner = Partner.objects.create(name="amp")
        self.moz_partner: Partner = Partner.objects.create(name="m0z-s@les")
        self.position1_alloc: AllocationSetting = AllocationSetting.objects.create(
            position=1
        )

        PartnerAllocation.objects.create(
            allocation_position=self.position1_alloc,
            partner=self.amp_partner,
            percentage=85,
        )
        PartnerAllocation.objects.create(
            allocation_position=self.position1_alloc,
            partner=self.moz_partner,
            percentage=15,
        )

        self.position2_alloc: AllocationSetting = AllocationSetting.objects.create(
            position=2
        )
        PartnerAllocation.objects.create(
            allocation_position=self.position2_alloc,
            partner=self.amp_partner,
            percentage=50,
        )
        PartnerAllocation.objects.create(
            allocation_position=self.position2_alloc,
            partner=self.moz_partner,
            percentage=50,
        )

    def test_filter_schema(self) -> None:
        """Tests filter schema for adM."""
        with open("./schema/adm_filter.schema.json", "r") as f:
            settings_schema = json.load(f)
            partner: Partner = Partner.objects.create(
                name="Partner Advertiser",
            )
            advertiser1: Advertiser = Advertiser.objects.create(
                name="Pocket", partner=partner
            )
            # we want to test that Advertiser names with special characters are valid
            advertiser2: Advertiser = Advertiser.objects.create(
                name="F!-reΩ fox+", partner=partner
            )
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

    def test_allocation_schema(self) -> None:
        """Tests partner allocation schema for SOV (Share of Voice)."""
        with open("./schema/allocation.schema.json", "r") as f:
            allocations_schema = json.load(f)
            allocations: dict[str, Any] = {}
            allocations.update({"name": "SOV-20230101140000", "allocations": []})

            allocations["allocations"] = [
                self.position1_alloc.to_dict(),
                self.position2_alloc.to_dict(),
            ]
            validate(allocations, allocations_schema)

    def test_too_many_allocation_raises_errors(self) -> None:
        """Tests partner allocation schema for SOV (Share of Voice) raise error with invalid."""
        with open("./schema/allocation.schema.json", "r") as f:
            allocations_schema = json.load(f)
            allocations: dict[str, Any] = {}
            allocations.update({"name": "SOV-20230101140000", "allocations": []})
            position3_alloc: AllocationSetting = AllocationSetting.objects.create(
                position=3
            )

            PartnerAllocation.objects.create(
                allocation_position=position3_alloc,
                partner=self.amp_partner,
                percentage=22,
            )
            PartnerAllocation.objects.create(
                allocation_position=position3_alloc,
                partner=self.moz_partner,
                percentage=78,
            )

            position4_alloc: AllocationSetting = AllocationSetting.objects.create(
                position=4
            )
            PartnerAllocation.objects.create(
                allocation_position=position4_alloc,
                partner=self.amp_partner,
                percentage=25,
            )
            PartnerAllocation.objects.create(
                allocation_position=position4_alloc,
                partner=self.moz_partner,
                percentage=75,
            )

            allocations["allocations"] = [
                self.position1_alloc.to_dict(),
                self.position2_alloc.to_dict(),
                position3_alloc.to_dict(),
                position4_alloc.to_dict(),
            ]
            with self.assertRaises(exceptions.ValidationError) as context:
                validate(allocations, allocations_schema)
            self.assertIn("4 is greater than the maximum of 3", str(context.exception))
