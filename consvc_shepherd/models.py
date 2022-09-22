from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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
        return f"{self.name}: {self.created_on}"

    def clean(self):
        if (
            not self.settings_type.is_active
            or self.settings_type.last_approved_by is None
        ):
            raise ValidationError("Partner Selected is not approved")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(SettingsSnapshot, self).save(*args, **kwargs)
