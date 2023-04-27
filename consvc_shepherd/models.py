from typing import Any

from django.contrib.auth import get_user_model
from django.db import models

from contile.models import Partner


class SettingsSnapshot(models.Model):
    name = models.CharField(max_length=128)
    settings_type = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True)
    json_settings = models.JSONField(blank=True, null=True)
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, blank=True, null=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    launched_by = models.ForeignKey(
        get_user_model(),
        related_name="launched_by",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    launched_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}: {self.created_on.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        return super(SettingsSnapshot, self).save(*args, **kwargs)


class AllocationSetting(models.Model):
    """Class that holds information for Allocation"""

    position = models.IntegerField(unique=True)

    def to_dict(self) -> dict[str, Any]:
        """Creates dictionary representation of AllocationSetting instance."""
        return {"position": self.position}

    def __str__(self):
        return f"Allocation Position : {self.position}"


class PartnerAllocation(models.Model):
    """Class that holds information about Partner Specific Allocation"""

    allocationPosition = models.ForeignKey(
        AllocationSetting, on_delete=models.CASCADE, related_name="partner_allocations"
    )
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True)
    percentage = models.IntegerField()

    def to_dict(self) -> dict[str, Any]:
        """Creates dictionary representation of PartnerAllocation instance."""
        partner_allocation_dict: dict = {}
        for allocation in self.partner_allocations.all():
            partner_allocation_dict.update(allocation.to_dict())
        return {"partner_allocations": partner_allocation_dict}
