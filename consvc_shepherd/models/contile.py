from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django_countries.fields import CountryField

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

    def is_valid_host_list(self, hostname_list):
        for hostname in hostname_list:
            if "." not in hostname or any(
                [not h.isalnum() for h in hostname.split(".")]
            ):
                raise ValidationError(
                    f"{hostname} is not a valid hostname, hostnames should only contain alpha numeric characters and '.'"
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
        super().clean()
        self.is_valid_host_list(self.click_hosts)
        self.is_valid_host_list(self.impression_hosts)

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
    domain = models.URLField()
    path = models.CharField(max_length=128)
    matching = models.BooleanField(choices=MATCHING_CHOICES, default=False)
    position = models.IntegerField(blank=True, null=True)

    # TODO validation goes here
    def clean(self) -> None:
        pass

    def __str__(self):
        return f"{self.geo}{self.domain}{self.path}"
