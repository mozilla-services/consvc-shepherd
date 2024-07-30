"""Ads Preview page"""

import json
import logging
import traceback
import uuid
from dataclasses import dataclass
from typing import TypedDict
from urllib.parse import SplitResult, quote, urlunsplit

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

DIRECT_SOLD_TILE_AD_TYPES = [3120]
SPOC_AD_TYPES = [2401, 3617]


class Region(TypedDict):
    """Represents a supported country or region within a country

    We use a TypedDict here instead of a dataclass for easy JSON serialization with json_script
    """

    code: str
    name: str


@dataclass(frozen=True)
class Environment:
    """Represents an Ads environment, not to be confused with a MARS or Shepherd environment."""

    code: str
    name: str
    mars_url: str
    spoc_site_id: int | None
    spoc_site_id_mobile: int | None
    spoc_zone_ids: list[int]
    direct_sold_tile_zone_ids: list[int]


@dataclass(frozen=True)
class Agent:
    """Struct for user agent"""

    code: str
    name: str
    is_mobile: bool


@dataclass(frozen=True)
class Spoc:
    """Model for a SPOC loaded from MARS"""

    image_src: str
    title: str
    domain: str
    excerpt: str
    sponsored_by: str
    sponsor: str
    url: str


@dataclass(frozen=True)
class Tile:
    """General Tile Model for Sponsored Tiles and Direct Sold Tiles loaded from MARS"""

    image_url: str
    name: str
    sponsored: str
    url: str


@dataclass(frozen=True)
class Ads:
    """Model for all the sets of ads that can be rendered in the preview template"""

    tiles: list[Tile]
    spocs: list[Spoc]
    is_mobile: bool


# Ad environments. Note that these differ from MARS or Shepherd environments.
ENVIRONMENTS: list[Environment] = [
    Environment(
        code="dev",
        name="Dev",
        mars_url="https://mars.stage.ads.nonprod.webservices.mozgcp.net",
        spoc_site_id=1276332,
        spoc_site_id_mobile=1276332,
        spoc_zone_ids=[307565],
        direct_sold_tile_zone_ids=[
            317828
        ],  # In Kevel > Network: MozAds-Dev, Site: Firefox Production corollary, Zone: Tiles
    ),
    Environment(
        code="preview",
        name="Preview",
        mars_url="https://mars.prod.ads.prod.webservices.mozgcp.net",
        spoc_site_id=1084367,
        spoc_site_id_mobile=1084367,
        spoc_zone_ids=[],
        direct_sold_tile_zone_ids=[
            319618
        ],  # In Kevel > Network: Pocket, Site: Firefox Staging, Zone: Tiles
    ),
    Environment(
        code="production",
        name="Production",
        mars_url="https://mars.prod.ads.prod.webservices.mozgcp.net",
        spoc_site_id=1070098,
        spoc_site_id_mobile=1240699,
        spoc_zone_ids=[217995],
        direct_sold_tile_zone_ids=[
            280143
        ],  # In Kevel > Network: Pocket, Site: Firefox Production, Zone: Tiles
    ),
    Environment(
        code="unified_dev",
        name="Dev Unified API",
        mars_url="https://mars.stage.ads.nonprod.webservices.mozgcp.net",
        spoc_site_id=None,
        spoc_site_id_mobile=None,
        spoc_zone_ids=[],
        direct_sold_tile_zone_ids=[],
    ),
    Environment(
        code="unified_prod",
        name="Prod Unified API",
        mars_url="https://mars.prod.ads.prod.webservices.mozgcp.net",
        spoc_site_id=None,
        spoc_site_id_mobile=None,
        spoc_zone_ids=[],
        direct_sold_tile_zone_ids=[],
    ),
]

AGENTS: list[Agent] = [
    Agent(
        code="Mozilla/5.0 (Windows NT 10.0; rv:10.0) Gecko/20100101 Firefox/91.0",
        name="Desktop",
        is_mobile=False,
    ),
    Agent(
        code="Mozilla/5.0 (Android 11; Mobile; rv:92.0) Gecko/92.0 Firefox/92.0",
        name="Mobile",
        is_mobile=True,
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


def load_regions() -> dict[str, list[Region]]:
    """Load Regions"""
    with open("./static/preview/iso-3166-2.json", "r") as file:
        data = json.load(file)
    country_codes = {country["code"] for country in COUNTRIES}
    regions = {}
    for country_code in country_codes:
        if country_code in data:
            country_data = data[country_code]
            region_list = []
            for division_code, division_name in country_data["divisions"].items():
                region_code = division_code.split("-")[1]
                region_name = division_name.split(" (")[0]
                region_list.append(Region(code=region_code, name=region_name))
            regions[country_code] = region_list
        else:
            logging.error("missing region data for ", country_code)

    return regions


REGIONS = load_regions()


def get_spocs_and_direct_sold_tiles(
    env: Environment, country: str, region: str, is_mobile: bool
) -> tuple[list[Tile], list[Spoc], bool]:
    """Load SPOCs and direct sold tiles from MARS for given country and region"""
    # Generate a unique pocket ID per request to avoid frequency capping
    pocket_id = uuid.uuid4()

    spoc_site_id = env.spoc_site_id
    if is_mobile:
        spoc_site_id = env.spoc_site_id_mobile

    body = {
        "pocket_id": f"{{{pocket_id}}}",  # Produces "{uuid}"
        "site": spoc_site_id,
        "version": 2,
        "country": country,
        "region": region,
        "placements": [
            {
                "name": "sponsored-topsite",
                "zone_ids": env.direct_sold_tile_zone_ids,
                "ad_types": DIRECT_SOLD_TILE_AD_TYPES,
            },
            {
                "name": "spocs",
                "zone_ids": env.spoc_zone_ids,
                "ad_types": SPOC_AD_TYPES,
            },
        ],
    }

    r = requests.post(f"{env.mars_url}/spocs", json=body, timeout=30)
    json = r.json()

    tiles = [
        Tile(
            image_url=create_image_url(tile["raw_image_src"], 48, 48),
            name=tile["title"],
            url=tile["url"],
            sponsored=LOCALIZATIONS["Sponsored"][country],
        )
        for tile in json.get("sponsored-topsite", [])
    ]

    spocs = [
        Spoc(
            image_src=spoc["image_src"],
            title=spoc["title"],
            domain=spoc["domain"],
            excerpt=spoc["excerpt"],
            url=spoc["url"],
            sponsored_by=localized_sponsored_by(spoc, country, is_mobile),
            sponsor=spoc.get("sponsor"),
        )
        for spoc in json.get("spocs", [])
    ]

    return (tiles, spocs, is_mobile)


def get_amp_tiles(
    env: Environment, country: str, region: str, agent: str
) -> list[Tile]:
    """Load Sponsored Tiles from MARS for given country and region"""
    params = {
        "country": country,
        "region": region,
    }

    headers = {
        "User-Agent": agent,
    }

    r = requests.get(
        f"{env.mars_url}/v1/tiles", params=params, headers=headers, timeout=30
    )
    return [
        Tile(
            image_url=tile["image_url"],
            name=tile["name"],
            url=tile["url"],
            sponsored=LOCALIZATIONS["Sponsored"][country],
        )
        for tile in r.json().get("tiles", [])
    ]


def get_unified(env: Environment, country: str, is_mobile: bool = False) -> Ads:
    """Load Ads from MARS unified api"""
    user_context_id = uuid.uuid4()

    # placement names will vary for preview and experiment environments, whereas
    # dev & prod have the same placements served by different kevel networks
    spocs_placement = "newtab_spocs"
    tiles_placement = "newtab_tiles"

    # load spocs & tiles, then map them to the same shape
    body = {
        "user_context_id": f"{user_context_id}",  # UUID -> str
        "placements": [
            {"placement": spocs_placement, "count": 10},
            {"placement": tiles_placement, "count": 3},
        ],
    }

    r = requests.post(f"{env.mars_url}/v1/ads", json=body, timeout=30)

    tiles = [
        Tile(
            image_url=tile["image_url"],
            name=tile["name"],
            url=tile["url"],
            sponsored=LOCALIZATIONS["Sponsored"][country],
        )
        for tile in r.json().get(tiles_placement, [])
    ]

    spocs = [
        Spoc(
            image_src=spoc["image_url"],
            title=spoc["title"],
            domain=spoc["domain"],
            excerpt=spoc["excerpt"],
            url=spoc["url"],
            sponsored_by=localized_sponsored_by(spoc, country, is_mobile),
            sponsor=spoc.get("sponsor"),
        )
        for spoc in r.json().get(spocs_placement, [])
    ]

    return Ads(spocs=spocs, tiles=tiles, is_mobile=is_mobile)


def get_ads(env: Environment, country: str, region: str, agent: Agent) -> Ads:
    """Based on Environment, either load spocs & tiles individually or from a single request"""
    if env.code.startswith("unified_"):
        return get_unified(env, country, agent.is_mobile)
    else:
        print("amp")
        amp_tiles = get_amp_tiles(env, country, region, agent.code)
        spocs_and_direct_sold_tiles = get_spocs_and_direct_sold_tiles(
            env, country, region, agent.is_mobile
        )

        return Ads(
            tiles=amp_tiles + spocs_and_direct_sold_tiles[0],
            spocs=spocs_and_direct_sold_tiles[1],
            is_mobile=agent.is_mobile,
        )


def localized_sponsored_by(
    spoc: dict[str, str], country: str, is_mobile: bool = False
) -> str:
    """Render the localized 'Sponsored by ...' text for a SPOC"""
    if (override := spoc.get("sponsored_by_override")) is not None:
        return override
    if is_mobile:
        return LOCALIZATIONS["Sponsored"][country].format(
            sponsor=spoc.get("sponsor"),
        )
    else:
        return LOCALIZATIONS["Sponsored by"][country].format(
            sponsor=spoc.get("sponsor"),
        )


def find_env_by_code(env_code: str) -> Environment:
    """Find an environment by code, raise an exception if no environment is found"""
    for env in ENVIRONMENTS:
        if env.code == env_code:
            return env

    raise ValueError(f"Unknown environment '{env_code}'")


def find_agent_by_code(agent_code: str) -> Agent:
    """Find an agent by code, raise an exception if no agent is found"""
    for agent in AGENTS:
        if agent.code == agent_code:
            return agent

    raise ValueError(f"Unknown agent '{agent_code}'")


def create_image_url(raw_image_src: str, w: int, h: int) -> str:
    """Modify an image url query parameters to the requested size.
    This function is intended to create image urls in the same way as FF newtab.
    See: https://hg.mozilla.org/mozilla-central/file/tip/browser/components/newtab/lib/TopSitesFeed.sys.mjs#l1058
    """
    size_path = "{}x{}".format(w, h)
    filters_path = "filters:format(jpeg):quality(60):no_upscale():strip_exif()"
    encoded_url = quote(raw_image_src)
    url_parts = SplitResult(
        "https",
        "img-getpocket.cdn.mozilla.net",
        size_path + "/" + filters_path + "/" + encoded_url,
        "",
        "",
    )
    return urlunsplit(url_parts)


class PreviewView(TemplateView):
    """View class for /preview"""

    template_name = "preview.html"

    def get(self, request, *args, **kwargs):
        """Render ad previews"""
        env_code = request.GET.get("env", "production")
        country = request.GET.get("country", "US")
        region = request.GET.get("region", "CA")
        agent_code = request.GET.get("agent", AGENTS[0].code)

        env = find_env_by_code(env_code)
        agent = find_agent_by_code(agent_code)

        debugMsg = f"{' &#x1F4F1; ' if agent.is_mobile else ''}country: {country}, region: {region}<br>env: {env}<br>{agent}"
        try:
            ads = get_ads(env, country, region, agent)
            debugMsg += "<br>&#x2705;ok"
        except Exception as e:
            ads = {}
            debugMsg += f"<br>&#x1F480;&#x1F480;&#x1F480; <br> {e}, <br> {traceback.format_exc()}"

        context = {
            "environments": ENVIRONMENTS,
            "countries": COUNTRIES,
            "regions": REGIONS,
            "environment": env_code,
            "country": country,
            "region": region,
            "agents": AGENTS,
            "agent": agent_code,
            "ads": ads,
            "debugMsg": debugMsg,
        }

        return self.render_to_response(context)
