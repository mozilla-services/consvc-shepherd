from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import BooleanField, CharField, ForeignKey
from django_countries.fields import CountryField

MATCHING_CHOICES = (
    (True, "exact"),
    (False, "prefix"),
)
INVALID_PREFIX_PATH_ERROR = "Prefix paths can't be just '/' but needs to end with '/' "
INVALID_PATH_ERROR = "All paths need to start '/'"


class Partner(models.Model):
    name: CharField = models.CharField(max_length=128)

    def to_dict(self):
        partner_dict = {}
        for advertiser in self.advertisers.all():
            partner_dict.update(advertiser.to_dict())

        return {"adm_advertisers": partner_dict}

    def __str__(self):
        return self.name


class Advertiser(models.Model):
    name: CharField = models.CharField(max_length=128)
    partner: ForeignKey = models.ForeignKey(
        Partner,
        blank=False,
        null=False,
        related_name="advertisers",
        on_delete=models.CASCADE,
    )

    def to_dict(self) -> dict[str, Any]:
        result: dict = {}
        geo_domain_combos = (
            self.ad_urls.all()
            .values_list("geo", "domain")
            .distinct()
            .order_by("geo", "domain")
        )

        for geo, domain in geo_domain_combos:
            ad_urls = self.ad_urls.filter(geo=geo, domain=domain).order_by("path")
            paths = [
                {
                    "value": ad_url.path,
                    "matching": ad_url.get_matching_display(),
                }
                for ad_url in ad_urls
            ]
            if geo not in result:
                result[geo] = []
            result[geo].append({"host": domain, "paths": paths})

        return {self.name: result}

    def __str__(self):
        return self.name


class AdvertiserUrl(models.Model):
    advertiser: ForeignKey = models.ForeignKey(
        Advertiser,
        blank=False,
        null=False,
        related_name="ad_urls",
        on_delete=models.CASCADE,
    )

    geo: CountryField = CountryField()
    domain: CharField = models.CharField(max_length=255)
    path: CharField = models.CharField(max_length=128)
    matching: BooleanField = models.BooleanField(choices=MATCHING_CHOICES, default=True)

    def __str__(self):
        return f"{self.geo.code}: {self.domain} {self.path}"

    def clean(self) -> None:
        is_valid_host(self.domain)
        if not self.path.startswith("/"):
            raise ValidationError(INVALID_PATH_ERROR)

        if self.get_matching_display() == "prefix" and (
            self.path == "/" or not self.path.endswith("/")
        ):
            raise ValidationError(INVALID_PREFIX_PATH_ERROR)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(AdvertiserUrl, self).save(*args, **kwargs)


def is_valid_host(host) -> None:

    if not all([h.isalnum() or h in [".", "-"] for h in host]):
        raise ValidationError(
            f"{host}: hostnames should only contain alpha numeric characters '-' and '.'"
        )
    if not 2 <= len(host.split(".")) <= 4 or "" in host.split("."):
        raise ValidationError(
            f"{host}: hostnames should have the structure <leaf-domain>.<second-level-domain>.<top-domain(s)>"
        )
