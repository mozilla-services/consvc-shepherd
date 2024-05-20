"""Template tag for localized 'Sponsored by ...' text for SPOCs."""

from django import template

from consvc_shepherd.preview import Spoc

LOCALIZATIONS = {
    "US": "Sponsored by {sponsor}",
    "CA": "Sponsored by {sponsor}",
    "DE": "Werbung von {sponsor}",
    "ES": "Patrocinado por {sponsor}",
    "FR": "Sponsorisé par {sponsor}",
    "GB": "Sponsored by {sponsor}",
    "IT": "Sponsorizzata da {sponsor}",
}

register = template.Library()


@register.filter(name="sponsored_by")
def sponsored_by(spoc: Spoc, country: str) -> str:
    """Render the localized 'Sponsored by ...' text for a SPOC"""
    if spoc.sponsored_by_override is not None:
        return spoc.sponsored_by_override

    return LOCALIZATIONS[country].format(sponsor=spoc.sponsor)
