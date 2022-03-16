from django.db import models
from django_countries.fields import CountryField
from django.contrib.postgres.fields import ArrayField

MATCHING_CHOICES = (
    (True, "exact"),
    (False, "prefix"),
)


class Partner(models.Model):
    name = models.CharField(max_length=128)
    click_hosts = ArrayField(
        models.CharField(max_length=128, blank=True, null=True),
        default=list,
        blank=True,
    )
    impression_hosts = ArrayField(
        models.CharField(max_length=128, blank=True, null=True),
        default=list,
        blank=True,
    )

    def __str__(self):
        return self.name


class Advertiser(models.Model):
    name = models.CharField(max_length=128)
    partner = models.ForeignKey(
        Partner,
        blank=False,
        null=False,
        related_name="advertisers",
        on_delete=models.CASCADE,
    )

    # TODO
    def to_dict(self):
        return {}

    def __str__(self):
        return self.name


class AdUrl(models.Model):
    geo = CountryField()
    domain = models.URLField()
    path = models.CharField(max_length=128)
    matching = models.BooleanField(choices=MATCHING_CHOICES, default=False)

    class Meta:
        abstract = True


class PartnerAdUrl(AdUrl):
    partner = models.ForeignKey(
        Partner,
        blank=False,
        null=False,
        related_name="default_ad_urls",
        on_delete=models.CASCADE,
    )

    # TODO validation goes here
    def clean(self) -> None:
        pass

    # TODO
    def to_dict(self) -> dict:
        return {}


class AdvertiserUrl(AdUrl):
    advertiser = models.ForeignKey(
        Advertiser,
        blank=False,
        null=False,
        related_name="ad_urls",
        on_delete=models.CASCADE,
    )

    position = models.IntegerField(blank=True, null=True)
    # TODO validation goes here
    def clean(self) -> None:
        pass

    # TODO
    def to_dict(self) -> dict:
        return {}
