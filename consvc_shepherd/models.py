"""Models module for consvc_shepherd."""

import json
from typing import Any

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import (
    CharField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    JSONField,
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
        Snopshot Name
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
