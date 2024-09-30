"""Models module for consvc_shepherd."""

import json
from typing import Any

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import (
    CharField,
    DateField,
    DateTimeField,
    FloatField,
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

    class CampaignType(models.TextChoices):
        """Represents the way a Boostr Product will be charged"""

        CPC = "CPC"
        CPM = "CPM"
        FLAT_FEE = "Flat Fee"
        NONE = "None"

    class Countries(models.TextChoices):
        """Defines country choices with full names for use in model fields."""

        US = "US", "United States"
        CA = "CA", "Canada"
        DE = "DE", "Germany"
        ES = "ES", "Spain"
        FR = "FR", "France"
        GB = "GB", "United Kingdom"
        IT = "IT", "Italy"
        PL = "PL", "Poland"
        AT = "AT", "Austria"
        NL = "NL", "Netherlands"
        LU = "LU", "Luxembourg"
        CH = "CH", "Switzerland"
        BE = "BE", "Belgium"

    boostr_id: IntegerField = models.IntegerField(unique=True)
    full_name: CharField = models.CharField()
    country: CharField = models.CharField(choices=Countries.choices, blank=True)
    campaign_type: CharField = models.CharField(
        choices=CampaignType.choices,
    )

    created_on: DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_on: DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the string representation for a Boostr Product"""
        return self.full_name


class BoostrDeal(models.Model):
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
        Currency symbol, eg "$"
    amount : IntegerField
        Amount
    sales_representatives : CharField
        Sales representative names as a comma separated list
    start_date: DateField
        Start date
    end_date: DateField
        End date
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
    name: CharField = models.CharField()
    advertiser: CharField = models.CharField()
    currency: CharField = models.CharField()
    amount: IntegerField = models.IntegerField()
    sales_representatives: CharField = models.CharField()
    start_date: DateField = models.DateField()
    end_date: DateField = models.DateField()
    products: ManyToManyField = models.ManyToManyField(
        BoostrProduct, related_name="products", through="BoostrDealProduct"
    )

    created_on: DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_on: DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the string representation for a Boostr Product"""
        return self.name


class BoostrDealProduct(models.Model):
    """Join table that represents the monthly budgets of every Product that is part of a Deal

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
    """

    boostr_deal: ForeignKey = models.ForeignKey(BoostrDeal, on_delete=models.CASCADE)
    boostr_product: ForeignKey = models.ForeignKey(
        BoostrProduct, on_delete=models.CASCADE
    )
    budget: IntegerField = models.IntegerField()
    month: CharField = models.CharField()


class BoostrSyncStatus(models.Model):
    """Table for capturing the status of a Booster sync process execution

    Attributes
    ----------
    synced_on : DateTimeField
        Date the Boostr sync process ran
    sync_status: CharField = models.CharField()
        The status of the symc process (success|failure)
    message: CharField = models.CharField()
        An optional error message populated when sync_status is "failure"
    """

    class SyncStatus(models.TextChoices):
        """Represents the status of a sync"""

        success = "success"
        failure = "failure"

    synced_on: DateTimeField = models.DateTimeField(auto_now=True)
    status: CharField = models.CharField(choices=SyncStatus.choices)
    message: CharField = models.CharField()


class Campaign(models.Model):
    """Representation of AdOps CampaignOverview

    Attributes
    ----------
    ad_ops_person : CharField
        Ad Ops Person
    notes : CharField
        Notes
    kevel_flight_id : IntegerField
        The kevel flight id
    net_spend : CharField
        Net Spend
    impressions_sold : IntegerField
        Impression Sold
    net_ecpm : FloatField
        Net eCPM
    seller : CharField
        Seller
    start_date: DateField
        Start date
    end_date: DateField
        End date
    created_on : DateTimeField
        Date of deal record creation (shepherd DB timestamp metadata, not boostr's)
    updated_on : DateTimeField
        Date of deal record update (shepherd DB timestamp metadata, not boostr's)

    Methods
    -------
    __str__(self)
        Return the string representation for a Boostr Campaign

    """

    ad_ops_person: CharField = models.CharField(null=True, blank=True)
    notes: CharField = models.CharField(null=True, blank=True)
    kevel_flight_id: IntegerField = models.IntegerField(null=True, blank=True)
    net_spend: IntegerField = models.IntegerField()
    impressions_sold: IntegerField = models.IntegerField()
    seller: CharField = models.CharField()
    deal: ForeignKey = models.ForeignKey(BoostrDeal, on_delete=models.CASCADE)
    start_date: DateField = models.DateField()
    end_date: DateField = models.DateField()
    created_on: DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_on: DateTimeField = models.DateTimeField(auto_now=True)

    @property
    def net_ecpm(self):
        """Calculate and return the net eCPM."""
        if self.impressions_sold and self.impressions_sold > 0:
            net_epcm_value = (self.net_spend / self.impressions_sold) * 1000
            return round(net_epcm_value, 2)
        return None

    class Meta:
        """Metadata for the Campaign model."""

        ordering = ["deal"]
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"

    def __str__(self):
        return f"Campaign {self.kevel_flight_id} - {self.ad_ops_person}"


class CampaignSummary(models.Model):
    """Model representing a summary of campaign metrics including Boostr, and kevel

    deal_id : IntegerField
        Boostr deal ID
    advertiser : CharField
        Advertiser Name
    net_spend : CharField
        Price of deal from Boostr
    impressions_sold : FloatField
        Number of impressions sold on Boostr
    clicks_delivered : IntegerField
        Number of clicks delivered from Glean(BQ)
    impressions_delivered : IntegerField
        Number of impressions delivered from Glean(BQ)

    """

    deal_id: IntegerField = models.IntegerField(primary_key=True)
    advertiser: CharField = models.CharField(max_length=255)
    net_spend: FloatField = models.FloatField()
    impressions_sold: FloatField = models.FloatField()
    clicks_delivered: IntegerField = models.IntegerField()
    impressions_delivered: IntegerField = models.IntegerField()

    @property
    def net_ecpm(self):
        """Calculate and return the net eCPM."""
        if self.impressions_sold and self.impressions_sold > 0:
            net_epcm_value = (self.net_spend / self.impressions_sold) * 1000
            return round(net_epcm_value, 2)
        return None

    @property
    def ctr(self):
        """Click-through rate = clicks_delivered / impressions_delivered"""
        if self.clicks_delivered and self.impressions_delivered > 0:
            ctr_value = (self.clicks_delivered / self.impressions_delivered) * 100
            return round(ctr_value, 2)
        return None

    @property
    def impressions_remaining(self):
        """Impressions_remaining = impressions_sold - impressions_delivered"""
        if self.impressions_sold > 0:
            return self.impressions_sold - self.impressions_delivered
        return 0

    @property
    def live(self):
        """Whether the campaign is active"""
        if self.impressions_delivered and self.impressions_delivered > 0:
            return "Yes"
        return "No"

    class Meta:
        """Metadata for the CampaignSummary model."""

        managed = False
        db_table = "campaign_summary_view"
        verbose_name = "Campaign"
        verbose_name_plural = "Campaign Summaries"


class DeliveredFlight(models.Model):
    """Representation of DeliveredFlight metrics obtained from BigQuery for various ad partners

    Attributes
    ----------
    submission_date : DateTimeField
        The date the metric was captured
    campaign_id : IntegerField
        Kevel campaign ID
    campaign_name : CharField
        Kevel campaign name
    flight_id : IntegerField
        Kevel flight ID
    flight_name : CharField
        Kevel flight name
    country : CharField
        Country where the metric was captured
    provider : Charfield
        Ad partner
    clicks_delivered : models.IntegerField
        The number of clicks delivered
    impression_delivered : models.IntegerField
        The number of impressions delivered

    Methods
    -------
    __str__(self)
        Return the string representation for a Delivered Flight

    """

    submission_date: DateField = models.DateField()
    campaign_id: IntegerField = models.IntegerField()
    campaign_name: CharField = models.CharField()
    flight_id: IntegerField = models.IntegerField()
    flight_name: CharField = models.CharField()
    country: CharField = models.CharField(null=True, blank=True)
    provider: CharField = models.CharField(null=True, blank=True)
    clicks_delivered: IntegerField = models.IntegerField()
    impressions_delivered: IntegerField = models.IntegerField()

    class Meta:
        """Metadata for the DeliveredFlight model."""

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "submission_date",
                    "campaign_id",
                    "flight_id",
                    "country",
                    "provider",
                ],
                name="unique_delivered_flight",
            ),
        ]

    def __str__(self):
        """Return the string representation for flight ids and associated number of clicks and impressions"""
        return f"{self.flight_id} : {self.clicks_delivered} clicks and {self.impressions_delivered} impressions"
