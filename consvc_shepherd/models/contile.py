from django.db import models
from django_countries.fields import CountryField
from django.contrib.postgres.fields import ArrayField

MATCHING_CHOICES = (
    (True, "exact"),
    (False, "prefix"),
)


class Advertiser(models.Model):
    name = models.CharField(max_length=128)

    # TODO
    def to_dict(self):
        return {}

    def __str__(self):
        return self.name


class AdvertiserUrl(models.Model):
    advertiser = models.ForeignKey(
        Advertiser,
        blank=False,
        null=False,
        related_name="ad_urls",
        on_delete=models.CASCADE,
    )

    # TODO might want to consider whether we want a subset of countries
    geo = CountryField()
    domain = models.URLField()
    path = models.CharField(max_length=128)
    matching = models.BooleanField(choices=MATCHING_CHOICES, default=False)
    click_hosts = ArrayField(
        models.CharField(max_length=128),
        blank=True,
        null=True,
    )
    impression_hosts = ArrayField(
        models.CharField(max_length=128),
        blank=True,
        null=True,
    )
    position = models.IntegerField(blank=True, null=True)
    # TODO validation goes here
    def clean(self) -> None:
        pass

    # TODO
    def to_dict(self) -> dict:
        return {}
