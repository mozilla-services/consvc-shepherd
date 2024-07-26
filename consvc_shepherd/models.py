"""Models module for consvc_shepherd."""

import json
from typing import Any

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import (
    CharField,
    DateField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    JSONField,
    ManyToManyField,
)

from contile.models import Partner


class SettingsSnapshot(models.Model):
    """SettingsSnapshot model for consvc_shepherd.

    Attributes
    ----------
    name : CharField
        Name of Snapshot
    settings_type :
        Partner associated with setting
    json_settings : JSONField
        JSON settings for snapshot
    created_by : ForeignKey
        User name of snapshot creator
    created_on : DateTimeField
        Date of snapshot creation
    launched_by : ForeignKey
        User name of who launches setting
    launched_date : DateTimeField
        Date of snapshot launch

    Methods
    -------
    __str__(self)
        Return string representation of Settings Snapshot
    """

    name: CharField = models.CharField(max_length=128)
    settings_type: ForeignKey = models.ForeignKey(
        Partner, on_delete=models.SET_NULL, null=True
    )
    json_settings: JSONField = models.JSONField(blank=True, null=True)
    created_by: ForeignKey = models.ForeignKey(
        get_user_model(),
        related_name="ss_created_by",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    created_on: DateTimeField = models.DateTimeField(auto_now_add=True)
    launched_by: ForeignKey = models.ForeignKey(
        get_user_model(),
        related_name="ss_launched_by",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    launched_date: DateTimeField = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        """Return string representation of SettingsSnapshot model."""
        return f"{self.name}: {self.created_on.strftime('%Y-%m-%d %H:%M')}"


class AllocationSettingsSnapshot(models.Model):
    """AllocationSettingsSnapshot model for consvc_shepherd.

    Attributes
    ----------
    name : CharField
        Snapshot Name
    json_settings : JSONField
        JSON settings for snapshot
    created_by : ForeignKey
        User name of snapshot creator
    created_on : DateTimeField
        Date of snapshot creation
    launched_by : ForeignKey
        User name of who launches setting
    launched_date : DateTimeField
        Date of snapshot launch

    Methods
    -------
    __str__(self)
        Return string representation of AllocationSetting model
    save(self)
        Save instance of the SettingsSnapshot model after validation
    """

    name: CharField = models.CharField(max_length=128)
    json_settings: JSONField = models.JSONField(blank=True, null=True)
    created_by: ForeignKey = models.ForeignKey(
        get_user_model(),
        related_name="alloc_ss_created_by",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    created_on: DateTimeField = models.DateTimeField(auto_now_add=True)
    launched_by: ForeignKey = models.ForeignKey(
        get_user_model(),
        related_name="alloc_ss_launched_by",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    launched_date: DateTimeField = models.DateTimeField(blank=True, null=True)

    @property
    def json_settings_formatted(self):
        """Pretty print json_settings."""
        return json.dumps(self.json_settings, indent=2)

    def __str__(self):
        return f"{self.name} - {self.created_on.strftime('%Y-%m-%d %H:%M')}"


class AllocationSetting(models.Model):
    """AllocationSetting model for consvc_shepherd.

    Attributes
    ----------
    position : IntegerField
        1-based position of AllocationSetting of Contile tile, left to right.

    Methods
    -------
    to_dict(self)
        Return AllocationSetting instance as a dictionary representation.
    __str__(self)
        Return string representation of AllocationSetting model
    """

    position: IntegerField = models.IntegerField(unique=True)

    def to_dict(self) -> dict[str, Any]:
        """Create dictionary representation of AllocationSetting instance.

        An allocation dictionary of all partner_allocations is created by calling
        each PartnerAllocation model's to_dict() method iteratively.  The result is a
        dictionary of a given position and the allocation between partners. See
        the  PartnerAllocation.to_dict() method for additional context.

        Returns
        -------
        dict[str, int | dict[str, int]]
        Ex. {"position": 1, "allocations" :[{"partner": "mozilla", "percentage": 100}]}
        """
        return {
            "position": self.position,
            "allocation": [
                allocation.to_dict() for allocation in self.partner_allocations.all()  # type: ignore [attr-defined]
            ],
        }

    def __str__(self):
        """Return string representation of AllocationSetting model."""
        return f"Allocation Position : {self.position}"


class PartnerAllocation(models.Model):
    """PartnerAllocation model for consvc_shepherd.

    Attributes
    ----------
    allocationPosition : AllocationSetting
        Foreign key pointer to AllocationSetting instance with
        related name of "partner_allocations"
    partner : Partner
        Foreign key pointing to Partner instance
    percentage : IntegerField
        Percentage of allocation (from 0 - 100)

    Methods
    -------
    to_dict(self)
        Return PartnerAllocation instance as a dictionary representation.
    """

    allocation_position: ForeignKey = models.ForeignKey(
        AllocationSetting, on_delete=models.CASCADE, related_name="partner_allocations"
    )
    partner: ForeignKey = models.ForeignKey(
        Partner, on_delete=models.CASCADE, null=True
    )
    percentage: IntegerField = models.IntegerField()

    def to_dict(self) -> dict[str, Any]:
        """Return PartnerAllocation instance as a dictionary representation.

        Example: {"partner": "mozilla", "percentage": 100}
        """
        return {"partner": self.partner.name, "percentage": self.percentage}


# Rename to SalesProduct?
class BoostrProduct(models.Model):
    """Representation of AdOps sales products that can be assigned to deals (many to many with deals)

    Attributes
    ----------
    boostr_id : IntegerField
        The product's id in Boostr
    full_name: CharField
        Product's full name
    campaign_type:
        Campaign type (CPC or CPM)
    created_on : DateTimeField
        Date of deal record creation (shepherd DB timestamp metadata, not boostr's)
    updated_on : DateTimeField
        Date of deal record update (shepherd DB timestamp metadata, not boostr's)

    Methods
    -------
    __str__(self)
        Return the string representation for a Boostr Product

    """

    boostr_id: IntegerField = models.IntegerField(unique=True)
    full_name: CharField = models.CharField(max_length=128)
    campaign_type: CharField = models.CharField(max_length=128)

    created_on: DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_on: DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the string representation for a Boostr Product"""
        return self.full_name


class BoostrDeal(models.Model):
    # Rename to SalesDeal? Or is the reference to Boostr helpful here?
    """Representation of AdOps sales deals pulled from Boostr

    Attributes
    ----------
    boostr_id : IntegerField
        The deal's id in Boostr
    name : CharField
        Deal name
    advertiser : CharField
        Advertiser name
    currency : CharField
        Currency code, ie "USD"
    amount : IntegerField
        Amount
    sales_representatives : CharField
        Sales representative names as a comma separated list
    campaign_type : CharField
        Campaign type (CPC or CPM)
    start_date: DateField
        Start date
    end_date: DateField
        End date
    created_on : DateTimeField
        Date of deal record creation (shepherd DB timestamp metadata, not boostr's)
    updated_on : DateTimeField
        Date of deal record update (shepherd DB timestamp metadata, not boostr's)
    """

    boostr_id: IntegerField = models.IntegerField(unique=True)
    name: CharField = models.CharField(max_length=128)
    advertiser: CharField = models.CharField(max_length=128)
    currency: CharField = models.CharField()  # Is there a django field for this?
    amount: IntegerField = models.IntegerField()
    sales_representatives: CharField = models.CharField(max_length=128)
    campaign_type: CharField = models.CharField()
    start_date: DateField = models.DateField()  # Or do we want datetime here? Boostr UI shows these as just dates so this might be sufficient.
    end_date: DateField = models.DateField()
    products: ManyToManyField = models.ManyToManyField(BoostrProduct, related_name='products', through='BoostrDealProduct')

    created_on: DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_on: DateTimeField = models.DateTimeField(auto_now=True)

class BoostrDealProduct(models.Model):
    """Join table that represents which Products are part of a deal, and their budgets

    Attributes
    ----------
    boostr_deal : BoostrDeal
        Foreign key pointer to BoostrDeal, with related name of deals
    boostr_product : Partner
        Foreign key pointing to BoostrProduct instance, with related name of products
    budget : IntegerField
        How much of the deal's overall budget is allocated to this product and month
    month: CharField
        The month when this product and budget combo will run

    Methods
    -------
    """

    boostr_deal: ForeignKey = models.ForeignKey(BoostrDeal, on_delete=models.CASCADE)
    boostr_product: ForeignKey = models.ForeignKey(BoostrProduct, on_delete=models.CASCADE)
    budget: IntegerField = models.IntegerField()
    month: CharField = models.CharField()
