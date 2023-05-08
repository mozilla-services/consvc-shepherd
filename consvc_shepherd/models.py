"""Models module for consvc_shepherd."""
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
    name: CharField = models.CharField(max_length=128)
    settings_type: ForeignKey = models.ForeignKey(
        Partner, on_delete=models.SET_NULL, null=True
    )
    json_settings: JSONField = models.JSONField(blank=True, null=True)
    created_by: ForeignKey = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, blank=True, null=True
    )
    created_on: DateTimeField = models.DateTimeField(auto_now_add=True)
    launched_by: ForeignKey = models.ForeignKey(
        get_user_model(),
        related_name="launched_by",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    launched_date: DateTimeField = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}: {self.created_on.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        return super(SettingsSnapshot, self).save(*args, **kwargs)


class AllocationSetting(models.Model):
    """Class that holds information for AllocationSetting."""

    position: IntegerField = models.IntegerField(unique=True)

    def to_dict(self) -> dict[str, Any]:
        """Creates dictionary representation of AllocationSetting instance."""
        allocations_dict: dict = {"position": self.position, "allocation": {}}
        for allocation in self.partner_allocations.all():  # type: ignore [attr-defined]
            allocations_dict["allocation"].update(allocation.to_dict())
        return allocations_dict

    def __str__(self):
        return f"Allocation Position : {self.position}"


class PartnerAllocation(models.Model):
    """Class that holds information about Partner Specific Allocation."""

    allocationPosition: ForeignKey = models.ForeignKey(
        AllocationSetting, on_delete=models.CASCADE, related_name="partner_allocations"
    )
    partner: ForeignKey = models.ForeignKey(
        Partner, on_delete=models.SET_NULL, null=True
    )
    percentage: IntegerField = models.IntegerField()

    def to_dict(self) -> dict[str, Any]:
        """Creates dictionary representation of PartnerAllocation instance."""
        return {self.partner.name: self.percentage}
