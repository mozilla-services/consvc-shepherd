from django.db import models
from django.contrib.auth import get_user_model


class SettingsSnapshot(models.Model):
    name = models.CharField(max_length=5, blank=True)
    json_settings = models.JSONField(blank=True, null=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                                   blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    launched_by = models.ForeignKey(get_user_model(),
                                    related_name="launched_by",
                                    on_delete=models.CASCADE, blank=True,
                                    null=True)

    def __str__(self):
        return f"{self.name}: {self.created_on}"
