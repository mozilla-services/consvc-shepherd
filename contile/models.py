from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django_countries.fields import CountryField

MATCHING_CHOICES = (
    (True, "exact"),
    (False, "prefix"),
)
INVALID_PREFIX_PATH_ERROR = "Prefix paths can't be just '/'"
INVALID_PATH_ERROR = "All paths need to start and end with '/'"


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

    def is_valid_host_list(self, hostname_list):
        for hostname in hostname_list:
            if "." not in hostname or any(
                [not h.isalnum() for h in hostname.split(".")]
            ):
                raise ValidationError(
                    f"{hostname} is not a valid hostnameasfasfsa hostnames should only contain alpha numeric characters and '.'"
                )

    def to_dict(self):
        partner_dict = {
            "DEFAULT": {
                "click_hosts": list(self.click_hosts),
                "impression_hosts": list(self.impression_hosts),
            }
        }
        for advertiser in self.advertisers.all():
            partner_dict.update(advertiser.to_dict())

        return partner_dict

    def clean(self):
        for c_host in self.click_hosts:
            is_valid_host(c_host)
        for i_host in self.impression_hosts:
            is_valid_host(i_host)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Partner, self).save(*args, **kwargs)

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

    def to_dict(self):
        result = {}
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
    advertiser = models.ForeignKey(
        Advertiser,
        blank=False,
        null=False,
        related_name="ad_urls",
        on_delete=models.CASCADE,
    )

    geo = CountryField()
    domain = models.CharField(max_length=255)
    path = models.CharField(max_length=128)
    matching = models.BooleanField(choices=MATCHING_CHOICES, default=False)
    position = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.geo.code}: {self.domain}{self.path}"

    def clean(self) -> None:
        is_valid_host(self.domain)
        if not (self.path.startswith("/") and self.path.endswith("/")):
            raise ValidationError(INVALID_PATH_ERROR)

        if self.get_matching_display() == "prefix" and self.path == "/":
            raise ValidationError(INVALID_PREFIX_PATH_ERROR)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(AdvertiserUrl, self).save(*args, **kwargs)


def is_valid_host(host):

    if not all([h.isalnum() or h in [".", "-"] for h in host]):
        raise ValidationError(
            f"{host}: hostnames should only contain alpha numeric characters '-' and '.'"
        )
    if not 2 <= len(host.split(".")) <= 3 or "" in host.split("."):
        raise ValidationError(
            f"{host}: hostnames should have the structure <leaf-domain>.<second-level-domain>.<top-domain> or <second-level-domain>.<top-domain>"
        )
