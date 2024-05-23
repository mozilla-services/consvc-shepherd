"""Ads Preview page"""
import uuid
from dataclasses import dataclass
from typing import TypedDict

import requests
from django.views.generic import TemplateView

# Localized strings from https://hg.mozilla.org/l10n-central/
#
# See e.g. https://hg.mozilla.org/l10n-central/es-ES/file/tip/browser/browser/newtab/newtab.ftl
# for Spanish (Spain).
LOCALIZATIONS = {
    "Sponsored": {
        "US": "Sponsored",
        "CA": "Sponsored",
        "DE": "Gesponsert",
        "ES": "Patrocinado",
        "FR": "Sponsorisé",
        "GB": "Sponsored",
        "IT": "Sponsorizzato",
    },
    "Sponsored by": {
        "US": "Sponsored by {sponsor}",
        "CA": "Sponsored by {sponsor}",
        "DE": "Werbung von {sponsor}",
        "ES": "Patrocinado por {sponsor}",
        "FR": "Sponsorisé par {sponsor}",
        "GB": "Sponsored by {sponsor}",
        "IT": "Sponsorizzata da {sponsor}",
    },
}


class Region(TypedDict):
    """Represents a supported country or region within a country

    We use a TypedDict here instead of a dataclass for easy JSON serialization with json_script
    """

    code: str
    name: str


@dataclass(frozen=True)
class Environment:
    """Represents a Site in Kevel. Some environments have more than one site configured."""

    code: str
    name: str
    mars_url: str
    spoc_site_id: int


@dataclass(frozen=True)
class Spoc:
    """Model for a SPOC loaded from MARS"""

    image_src: str
    title: str
    domain: str
    excerpt: str
    sponsored_by: str


@dataclass(frozen=True)
class Tile:
    """Model for a Sponsored Tile loaded from MARS"""

    image_url: str
    name: str
    sponsored: str


# Ad environments. Note that these differ from MARS or Shepherd environments.
ENVIRONMENTS: list[Environment] = [
    Environment(
        code="dev",
        name="Dev",
        mars_url="https://mars.stage.ads.nonprod.webservices.mozgcp.net",
        spoc_site_id=1276332,
    ),
    Environment(
        code="preview",
        name="Preview",
        mars_url="https://mars.prod.ads.prod.webservices.mozgcp.net",
        spoc_site_id=1084367,
    ),
    Environment(
        code="production",
        name="Production",
        mars_url="https://mars.prod.ads.prod.webservices.mozgcp.net",
        spoc_site_id=1070098,
    ),
]

COUNTRIES: list[Region] = [
    Region(code="US", name="United States"),
    Region(code="CA", name="Canada"),
    Region(code="DE", name="Germany"),
    Region(code="ES", name="Spain"),
    Region(code="FR", name="France"),
    Region(code="GB", name="United Kingdom"),
    Region(code="IT", name="Italy"),
]

REGIONS: dict[str, list[Region]] = {
    "US": [
        Region(code="AL", name="Alabama"),
        Region(code="AK", name="Alaska"),
        Region(code="AZ", name="Arizona"),
        Region(code="AR", name="Arkansas"),
        Region(code="CA", name="California"),
        Region(code="CO", name="Colorado"),
        Region(code="CT", name="Connecticut"),
        Region(code="DE", name="Delaware"),
        Region(code="DC", name="District of Columbia"),
        Region(code="FL", name="Florida"),
        Region(code="GA", name="Georgia"),
        Region(code="HI", name="Hawaii"),
        Region(code="ID", name="Idaho"),
        Region(code="IL", name="Illinois"),
        Region(code="IN", name="Indiana"),
        Region(code="IA", name="Iowa"),
        Region(code="KS", name="Kansas"),
        Region(code="KY", name="Kentucky"),
        Region(code="LA", name="Louisiana"),
        Region(code="ME", name="Maine"),
        Region(code="MD", name="Maryland"),
        Region(code="MA", name="Massachusetts"),
        Region(code="MI", name="Michigan"),
        Region(code="MN", name="Minnesota"),
        Region(code="MS", name="Mississippi"),
        Region(code="MO", name="Missouri"),
        Region(code="MT", name="Montana"),
        Region(code="NE", name="Nebraska"),
        Region(code="NV", name="Nevada"),
        Region(code="NH", name="New Hampshire"),
        Region(code="NJ", name="New Jersey"),
        Region(code="NM", name="New Mexico"),
        Region(code="NY", name="New York"),
        Region(code="NC", name="North Carolina"),
        Region(code="ND", name="North Dakota"),
        Region(code="OH", name="Ohio"),
        Region(code="OK", name="Oklahoma"),
        Region(code="OR", name="Oregon"),
        Region(code="PA", name="Pennsylvania"),
        Region(code="RI", name="Rhode Island"),
        Region(code="SC", name="South Carolina"),
        Region(code="SD", name="South Dakota"),
        Region(code="TN", name="Tennessee"),
        Region(code="TX", name="Texas"),
        Region(code="UT", name="Utah"),
        Region(code="VT", name="Vermont"),
        Region(code="VA", name="Virginia"),
        Region(code="WA", name="Washington"),
        Region(code="WV", name="West Virginia"),
        Region(code="WI", name="Wisconsin"),
        Region(code="WY", name="Wyoming"),
    ],
    "CA": [
        Region(code="AB", name="Alberta"),
        Region(code="BC", name="British Columbia"),
        Region(code="MB", name="Manitoba"),
        Region(code="NB", name="New Brunswick"),
        Region(code="NL", name="Newfoundland and Labrador"),
        Region(code="NS", name="Nova Scotia"),
        Region(code="ON", name="Ontario"),
        Region(code="PE", name="Prince Edward Island"),
        Region(code="QC", name="Quebec"),
        Region(code="SK", name="Saskatchewan"),
        Region(code="NT", name="Northwest Territories"),
        Region(code="NU", name="Nunavut"),
        Region(code="YT", name="Yukon"),
    ],
}


def get_spocs(env: Environment, country: str, region: str) -> list[Spoc]:
    """Load SPOCs from MARS for given country and region"""
    # Generate a unique pocket ID per request to avoid frequency capping
    pocket_id = uuid.uuid4()

    body = {
        "pocket_id": f"{{{pocket_id}}}",  # produces "{uuid}"
        "site": env.spoc_site_id,
        "version": 2,
        "country": country,
        "region": region,
        # Omit placements to use server-side defaults
    }

    r = requests.post(f"{env.mars_url}/spocs", json=body, timeout=30)

    return [
        Spoc(
            image_src=spoc["image_src"],
            title=spoc["title"],
            domain=spoc["domain"],
            excerpt=spoc["excerpt"],
            sponsored_by=localized_sponsored_by(spoc, country),
        )
        for spoc in r.json().get("spocs", [])
    ]


def get_tiles(env: Environment, country: str, region: str) -> list[Tile]:
    """Load Sponsored Tiles from MARS for given country and region"""
    params = {
        "country": country,
        "region": region,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
    }

    r = requests.get(f"{env.mars_url}/v1/tiles", params=params, headers=headers, timeout=30)

    return [
        Tile(
            image_url=tile["image_url"],
            name=tile["name"],
            sponsored=LOCALIZATIONS["Sponsored"][country],
        )
        for tile in r.json().get("tiles", [])
    ]


def localized_sponsored_by(spoc: dict[str, str], country: str) -> str:
    """Render the localized 'Sponsored by ...' text for a SPOC"""
    if (override := spoc.get("sponsored_by_override")) is not None:
        return override

    return LOCALIZATIONS["Sponsored by"][country].format(
        sponsor=spoc.get("sponsor"),
    )


def find_env_by_code(env_code: str) -> Environment:
    for env in ENVIRONMENTS:
        if env.code == env_code:
            return env

    raise ValueError(f"Unknown environment '{env_code}'")


class PreviewView(TemplateView):
    """View class for /preview"""

    template_name = "preview.html"

    def get(self, request, *args, **kwargs):
        """Render ad previews"""
        env_code = request.GET.get("env", "production")
        country = request.GET.get("country", "US")
        region = request.GET.get("region", "CA")

        env = find_env_by_code(env_code)

        context = {
            "environments": ENVIRONMENTS,
            "countries": COUNTRIES,
            "regions": REGIONS,
            "environment": env_code,
            "country": country,
            "region": region,
            "spocs": get_spocs(env, country, region),
            "tiles": get_tiles(env, country, region),
        }

        return self.render_to_response(context)
