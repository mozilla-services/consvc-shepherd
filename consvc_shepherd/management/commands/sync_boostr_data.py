"""Django admin custom command for fetching and saving Deal and Product data from Boostr to Shepherd"""

import logging
import math
import traceback
import time
from pathlib import Path
from time import sleep
from typing import Any

import environ
import requests
from django.core.management.base import BaseCommand

from consvc_shepherd.models import (
    BoostrDeal,
    BoostrDealProduct,
    BoostrProduct,
    BoostrSyncStatus,
)

MAX_DEAL_PAGES_DEFAULT = 50
SYNC_STATUS_SUCCESS = "success"
SYNC_STATUS_FAILURE = "failure"
REQUEST_INTERVAL_SECONDS_DEFAULT = 1
DEFAULT_OPTIONS = {
    "request_interval_seconds": REQUEST_INTERVAL_SECONDS_DEFAULT,
    "max_deal_pages": MAX_DEAL_PAGES_DEFAULT,
}


class Command(BaseCommand):
    """Django admin custom command for fetching and saving Deal and Product data from Boostr to Shepherd"""

    help = "Run a script that calls the Boostr API and saves Deals and Products from Boostr"

    def add_arguments(self, parser):
        """Register expected command line arguments"""
        parser.add_argument(
            "base_url",
            type=str,
            help="The base url for the Boostr API, eg. https://app.boostr.com/api",
        )
        parser.add_argument(
            "--max-deal-pages",
            default=MAX_DEAL_PAGES_DEFAULT,
            type=int,
            help=f"""By default, the sync code will stop trying to fetch additional deals pages after
                {MAX_DEAL_PAGES_DEFAULT} pages. Currently we have ~14 pages of deals in Boostr, so this default max
                should be sufficient for a while.""",
        )
        parser.add_argument(
            "--request-interval-seconds",
            default=REQUEST_INTERVAL_SECONDS_DEFAULT,
            type=int,
            help=f"""This parameter controls the rate of requests to the Boostr API in order to stay under their rate
                limits. By default, the sync code will wait {REQUEST_INTERVAL_SECONDS_DEFAULT} seconds between
                requests.""",
        )

    def handle(self, *args, **options):
        """Handle running the command"""
        env = environ.Env()
        BASE_DIR = Path(__file__).resolve().parent.parent
        environ.Env.read_env(BASE_DIR / ".env")

        loader = BoostrLoader(
            options["base_url"],
            env("BOOSTR_API_EMAIL"),
            env("BOOSTR_API_PASS"),
            options,
        )
        loader.load()


class BoostrApiError(Exception):
    """Raise this error whenever we don't get a 200 status back from boostr"""

    pass


class BoostrApi:
    """Wrap up interactions with the Boostr API into a convenient class that handles the session, rate limits, etc"""

    base_url: str
    session: requests.Session
    request_interval_seconds: int

    def __init__(
        self, base_url: str, email: str, password: str, options=DEFAULT_OPTIONS
    ):
        self.base_url = base_url
        self.request_interval_seconds = options.get(
            "request_interval_seconds", REQUEST_INTERVAL_SECONDS_DEFAULT
        )
        self.setup_session(email, password)

    def setup_session(self, email: str, password: str) -> None:
        """Authenticate with the boostr api and create and store a session on the instance"""
        headers = {
            "Accept": "application/vnd.boostr.public",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(headers)
        token = self.authenticate(email, password)
        headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update(headers)

    def authenticate(self, email: str, password: str) -> str:
        """Authenticate with the Boostr API and return jwt"""
        post_data = {"auth": {"email": email, "password": password}}
        token = self.post("user_token", post_data)
        return str(token["jwt"])

    def post(self, path: str, json=None, headers=None) -> Any:
        """Make POST requests to Boostr that uses the session, pass through headers and json data,
        check status, and return parsed json
        """
        if json is None:
            json = {}
        if headers is None:
            headers = {}

        response = self.session.post(
            f"{self.base_url}/{path}",
            json=json,
            headers=headers,
            timeout=15,
        )

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60)) + 1
            time.sleep(retry_after)
            return self.post(path, json, headers)

        if not response.ok:
            raise BoostrApiError(
                f"Bad response status {response.status_code} from /{path}: {response}"
            )
        json = response.json()
        return json

    def get(self, path: str, params=None, headers=None):
        """Make GET requests to Boostr that use the session, pass through headers and query params,
        check status, and return parsed json
        """
        if params is None:
            params = {}
        if headers is None:
            headers = {}

        response = self.session.get(
            f"{self.base_url}/{path}", params=params, headers=headers, timeout=15
        )
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60)) + 1
            time.sleep(retry_after)
            return self.get(path, params, headers)

        if not response.ok:
            raise BoostrApiError(
                f"Bad response status {response.status_code} from /{path}: {response}"
            )
        json = response.json()
        return json


class BoostrLoader:
    """Wrap up interaction with the Boostr API"""

    boostr: BoostrApi
    log: logging.Logger
    max_deal_pages: int

    def __init__(
        self, base_url: str, email: str, password: str, options=DEFAULT_OPTIONS
    ):
        self.log = logging.getLogger("sync_boostr_data")
        self.boostr = BoostrApi(base_url, email, password, options)
        self.max_deal_pages = options.get("max_deal_pages", MAX_DEAL_PAGES_DEFAULT)

    def upsert_products(self) -> None:
        """Fetch all Boostr products and upsert them to Shepherd DB"""
        products_params = {
            "per": "300",
            "page": "1",
            "filter": "all",
        }
        products = self.boostr.get("products", params=products_params)
        self.log.info(f"Fetched {(len(products))} products")

        for product in products:
            BoostrProduct.objects.update_or_create(
                boostr_id=product["id"],
                defaults={
                    "full_name": product["full_name"],
                    "country": get_country(product["full_name"]),
                    "campaign_type": get_campaign_type(product["full_name"]),
                },
            )
        self.log.info(f"Upserted {(len(products))} products")

    def upsert_deals(self) -> None:
        """Fetch all Boostr deals and upsert the Closed Won ones to Shepherd DB"""
        page = 0
        deals_params = {
            "per": "300",
            "page": str(page),
            "filter": "all",
        }
        while page < self.max_deal_pages:
            page += 1
            deals_params["page"] = str(page)

            deals = self.boostr.get("deals", params=deals_params)
            self.log.info(f"Fetched {len(deals)} deals for page {page}")

            # Paged through all available records and are getting an empty list back
            if len(deals) == 0:
                self.log.info(f"Done. Fetched all the deals in {page - 1} pages")
                break

            closed_won_deals = [d for d in deals if (d["stage_name"] == "Closed Won")]
            for deal in closed_won_deals:
                boostr_deal, _ = BoostrDeal.objects.update_or_create(
                    boostr_id=deal["id"],
                    name=deal["name"],
                    advertiser=deal["advertiser_name"],
                    currency=deal["currency"],
                    amount=math.floor(float(deal["budget"])),
                    sales_representatives=",".join(
                        str(d["email"]) for d in deal["deal_members"]
                    ),
                    start_date=deal["start_date"],
                    end_date=deal["end_date"],
                )
                self.log.debug(f"Upserted deal: {deal['id']}")

                self.upsert_deal_products(boostr_deal)
                self.log.info(f"Upserted products and budgets for deal: {deal['id']}")
            # If this is the last iteration of the loop due to the max page limit, log that we stopped
            if page >= self.max_deal_pages:
                self.log.info(
                    f"Done. Stopped fetching deals after hitting max_page_limit of {page} pages."
                )

    def upsert_deal_products(self, deal: BoostrDeal) -> None:
        """Fetch the deal_products for a particular deal and store them in our DB with their monthly budgets"""
        deal_products = self.boostr.get(f"deals/{deal.boostr_id}/deal_products")

        self.log.debug(
            f"Fetched {len(deal_products)} deal_products for deal: {deal.boostr_id}"
        )

        for deal_product in deal_products:
            product = BoostrProduct.objects.get(boostr_id=deal_product["product"]["id"])
            for budget in deal_product["deal_product_budgets"]:
                BoostrDealProduct.objects.update_or_create(
                    boostr_deal=deal,
                    boostr_product=product,
                    month=budget["month"],
                    budget=budget["budget"],
                )
            self.log.debug(
                f'Upserted {len(deal_product["deal_product_budgets"])} months of budget for product: '
                f"{product.boostr_id} to deal: {deal.boostr_id}"
            )

    def update_sync_status(self, status, message=None):
        """Fupdate the BoostrSyncStatus table given the status and the message"""
        BoostrSyncStatus.objects.create(
            status=status,
            message=message,
        )

    def load(self):
        """Loader entry point"""
        try:
            self.upsert_products()
            self.upsert_deals()
            self.log.info(
                "Boostr sync process completed successfully. Updating sync_status"
            )
            self.update_sync_status(SYNC_STATUS_SUCCESS)
        except Exception as e:
            error = f"Exception: {str(e):} Trace: {traceback.format_exc()}"
            self.log.error(
                f"Boostr sync process encountered an error: {error}. Updating sync_status"
            )
            self.update_sync_status(
                SYNC_STATUS_FAILURE,
                f"Exception: {str(e):} Trace: {traceback.format_exc()}",
            )
            raise e


def get_campaign_type(product_full_name: str) -> str:
    """Infer a campaign type from a product's full name"""
    if "CPC" in product_full_name:
        return BoostrProduct.CampaignType.CPC
    if "CPM" in product_full_name:
        return BoostrProduct.CampaignType.CPM
    if "Flat Fee" in product_full_name:
        return BoostrProduct.CampaignType.FLAT_FEE
    else:
        return BoostrProduct.CampaignType.NONE


def get_country(product_full_name: str) -> str:
    """Return the country code found in the product's full name."""
    # Mapping of common country code abbreviations to standardized ISO 3166-1 alpha-2 codes
    country_code_map = {
        "US": "US",
        "CA": "CA",
        "DE": "DE",
        "ES": "ES",
        "FR": "FR",
        "GB": "GB",
        "UK": "GB",  # Map "UK" to "GB" for United Kingdom
        "IT": "IT",
        "PL": "PL",
        "AT": "AT",
        "NL": "NL",
        "LU": "LU",
        "CH": "CH",
        "BE": "BE",
        "SP": "ES",  # Map "SP" to "ES" for Spain
    }

    normalized_name = product_full_name.upper()
    words = set(normalized_name.split())

    for code in country_code_map:
        if code in words:
            return country_code_map[code]

    # Return an empty string if no country code is found
    return ""
