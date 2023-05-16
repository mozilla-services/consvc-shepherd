"""Models for consvc_shepherd/contile."""
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import BooleanField, CharField, ForeignKey
from django_countries.fields import CountryField

MATCHING_CHOICES: tuple[tuple[bool, str], tuple[bool, str]] = (
    (True, "exact"),
    (False, "prefix"),
)
INVALID_PREFIX_PATH_ERROR: str = (
    "Prefix paths can't be just '/' but needs to end with '/' "
)
INVALID_PATH_ERROR: str = "All paths need to start '/'"


class Partner(models.Model):
    """Partner model for consvc_shepherd/contile.

    Methods
    -------
    to_dict(self)
        Convert Advertiser instances into a single dictionary object.
    __str__(self)
        Return string representation of Partner model.
    """

    name: CharField = models.CharField(max_length=128)

    def to_dict(self) -> dict[str, Any]:
        """Convert Advertiser instances into a single dictionary object.

        A partner dictionary of all advertiser instances is created by calling
        each Advertiser model's to_dict() method iteratively.  The result is a
        dictionary of dictionaries, each mapping to individual advertisers. See
        the  Advertiser.to_dict() method for additional context.

        Returns
        -------
        dict
            a dictionary mapping of adm_advertisers to each advertiser dictionary object.
        """
        partner_dict = {}
        for advertiser in self.advertisers.all():  # type: ignore [attr-defined]
            partner_dict.update(advertiser.to_dict())

        return {"adm_advertisers": partner_dict}

    def __str__(self):
        """Return string representation of Partner model."""
        return self.name


class Advertiser(models.Model):
    """Advertiser model for consvc_shepherd/contile.

    Methods
    -------
    __str__(self)
        Return string representation of Advertiser model
    """

    name: CharField = models.CharField(max_length=128)
    partner: ForeignKey = models.ForeignKey(
        Partner,
        blank=False,
        null=False,
        related_name="advertisers",
        on_delete=models.CASCADE,
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert Advertiser instance into a single dictionary object.

        Creates a dictionary object that has a key of the advertiser name and the value is
        a dictionary object containing the following advertiser attributes:

            advertiser : Advertiser
            path : str
            matching : bool
            domain : str
            geo : str

        Returns
        -------
        dict
            a dictionary mapping of the advertiser name to a dictionary object of attributes.
        """
        result: dict = {}
        geo_domain_combos = (
            self.ad_urls.all()  # type: ignore [attr-defined]
            .values_list("geo", "domain")
            .distinct()
            .order_by("geo", "domain")
        )

        for geo, domain in geo_domain_combos:
            ad_urls = self.ad_urls.filter(geo=geo, domain=domain).order_by(  # type: ignore [attr-defined]
                "path"
            )
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
        """Return string representation of Advertiser model."""
        return self.name


class AdvertiserUrl(models.Model):
    """Class for AdvertiserUrl model.

    Methods
    -------
    __str__(self)
        Return string representation of AdvertiserUrl
    clean(self)
        Check that path and domain fields conform to defined format.
    save(self)
        Save instance of the AdvertiserUrl model after validation.
    """

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

    def __str__(self) -> str:
        """Return string representation of AdvertiserUrl model."""
        return f"{self.geo.code}: {self.domain} {self.path}"

    def clean(self) -> None:
        """Check that path and domain fields conform to defined format.

        Raises
        ------
        ValidationError
            If path does not start with '/', end with '/' or is a '/' only.

        """
        is_valid_host(self.domain)
        if not self.path.startswith("/"):
            raise ValidationError(INVALID_PATH_ERROR)

        if self.get_matching_display() == "prefix" and (  # type: ignore [attr-defined]
            self.path == "/" or not self.path.endswith("/")
        ):
            raise ValidationError(INVALID_PREFIX_PATH_ERROR)

    def save(self, *args, **kwargs):
        """Save instance of the AdvertiserUrl model after validation.

        Whenever an instance of AdvertiserUrl is created or updated, this
        override save() method is run. This allows for some logic to be
        run prior to storing data. In this case, running full_clean().

        Returns
        -------
        AdvertiserUrl
            Saved instance of AdvertiserUrl model.
        """
        self.full_clean()
        return super(AdvertiserUrl, self).save(*args, **kwargs)


def is_valid_host(host: str) -> None:
    """Check if host conforms to valid structure and allowable characters.

    Parameters
    ----------
    host : str
        The host domain string

    Raises
    ------
    ValidationError
        If hostname contains non-alphanumeric including '-' and '.'
        or
        does not conform to structure: <leaf-domain>.<second-level-domain>.<top-domain(s)>
    """
    if not all([h.isalnum() or h in [".", "-"] for h in host]):
        raise ValidationError(
            f"{host}: hostnames should only contain alphanumeric characters '-' and '.'"
        )
    if not 2 <= len(host.split(".")) <= 4 or "" in host.split("."):
        raise ValidationError(
            f"{host}: hostnames should have the structure <leaf-domain>.<second-level-domain>.<top-domain(s)>"
        )
