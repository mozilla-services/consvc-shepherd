"""Django admin custom command for fetching and saving Deal and Product data from Boostr to Shepherd"""

import json
import logging
import math
import os
import pprint
from time import sleep
import time

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Any

import environ
import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from consvc_shepherd.models import BoostrDeal, BoostrDealProduct, BoostrProduct

env = environ.Env()
MAX_DEAL_PAGES_DEFAULT = 50


@dataclass(frozen=True)
class NewBoostrDealMediaPlanLineItem:
    """TODO"""

    media_plan_line_item_id: int
    # media_plan_id: int
    boostr_deal: int
    boostr_product: int
    rate_type: str
    rate: Decimal
    quantity: Decimal
    budget: Decimal
    month: str

    def __str__(self) -> str:
        return f"{self.boostr_product}"


@dataclass
class NewBoostrMediaPlan:
    """Media Plan For Boostr Deals"""

    media_plan_id: int
    name: str
    boostr_deal: int
    line_items: Dict[
        int,
        Dict[int, List[NewBoostrDealMediaPlanLineItem]],
    ] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.name}"

    def add_line_item(self, line_item: NewBoostrDealMediaPlanLineItem):
        """Add a line item to a media plan"""
        # if line_item.media_plan_line_item_id not in self.line_items:
        if self.boostr_deal not in self.line_items:
            self.line_items[self.boostr_deal] = {}
        if line_item.boostr_product not in self.line_items[self.boostr_deal]:
            self.line_items[self.boostr_deal][line_item.boostr_product] = []
            self.line_items[self.boostr_deal][line_item.boostr_product].append(
                line_item
            )

    def find_line_item(
        self, boostr_deal: int, boostr_product: int
    ) -> List[NewBoostrDealMediaPlanLineItem]:
        """Find a line item using the boostr id and product id"""
        return self.line_items.get(boostr_deal, {}).get(boostr_product, [])


@dataclass
class MediaPlanCollection:
    """A collection for storing Media Plans"""

    media_plans: Dict[int, NewBoostrMediaPlan] = field(default_factory=dict)

    def add_media_plan(self, boostr_plan: int, media_plan: NewBoostrMediaPlan):
        """Add a media plan to the collection"""
        if boostr_plan not in self.media_plans:
            self.media_plans[boostr_plan] = media_plan


class Command(BaseCommand):
    """Django admin custom command for fetching and saving Deal and Product data from Boostr to Shepherd"""

    help = "Run a script that calls the Boostr API and saves Deals and Products from Boostr"

    def add_arguments(self, parser):
        """Register expected command line arguments"""
        parser.add_argument(
            "base_url",
            type=str,
            help="The base url for the Boostr API, eg. https://app.boostr.com/api/",
        )
        parser.add_argument(
            "email",
            type=str,
            help="The email for the Boostr API account to authenticate with (see 1password Ads Eng vault)",
        )
        parser.add_argument(
            "password",
            type=str,
            help="The password for the Boostr API account (see 1password Ads Eng vault)",
        )
        parser.add_argument(
            "--max-deal-pages",
            default=MAX_DEAL_PAGES_DEFAULT,
            type=int,
            help=f"""By default, the sync code will stop trying to fetch additional deals pages after
                {MAX_DEAL_PAGES_DEFAULT} pages. Currently we have ~14 pages of deals in Boostr, so this default max
                should be sufficient for a while.""",
        )

    def handle(self, *args, **options):
        """Handle running the command"""
        loader = BoostrLoader(
            options["base_url"],
            options["email"],
            options["password"],
            options["max_deal_pages"],
        )
        loader.load()


class BoostrApiError(Exception):
    """Raise this error whenever we don't get a 200 status back from boostr"""

    pass


class BoostrApi:
    """Wrap up interactions with the Boostr API into a convenient class that handles the session, rate limits, etc"""

    base_url: str
    session: requests.Session
    log: logging.Logger

    def __init__(self, base_url: str, email: str, password: str):
        self.log = logging.getLogger("sync_boostr_data")
        self.base_url = base_url
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
            self.post(path, json, headers)

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
            self.log.info(f"{response.headers}")
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

    line_items: Dict[int, NewBoostrDealMediaPlanLineItem]
    current_dir = os.path.dirname(__file__)
    json_file = os.path.join(current_dir, "mediaplans.json")
    li_json_file = os.path.join(current_dir, "mp_lineitems.json")
    mpc = MediaPlanCollection()

    with open(json_file, "r") as file:
        mp_data = json.load(file)

    try:
        with open(li_json_file, "r") as file:
            li_mp_data = json.load(file)
            # pprint.pprint(li_mp_data)
    except Exception:
        li_mp_data = []

    def __init__(self, base_url: str, email: str, password: str, max_deal_pages=50):
        self.log = logging.getLogger("sync_boostr_data")
        self.boostr = BoostrApi(base_url, email, password)
        self.max_deal_pages = max_deal_pages

    def append_json_file(self, new_data: str, json_file: str):
        """Append JSON to file to save API response for later use"""
        try:
            with open(json_file, "r") as file:
                li_mp_data = json.load(file)
        except Exception:
            li_mp_data = []

        li_mp_data.extend(new_data)

        with open(json_file, "w") as file:
            json.dump(li_mp_data, file, indent=4)

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
                full_name=product["full_name"],
                campaign_type=get_campaign_type(product["full_name"]),
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

                # self.upsert_deal_products()
                self.log.info(f"Upserted products and budgets for deal: {deal['id']}")
            # If this is the last iteration of the loop due to the max page limit, log that we stopped
            if page >= self.max_deal_pages:
                self.log.info(
                    f"Done. Stopped fetching deals after hitting max_page_limit of {page} pages."
                )

    def upsert_deal_products(self) -> None:
        """Fetch the deal_products for multiple and store them in our DB with their monthly budgets"""
        page = 0
        deals_product_params = {
            "per": "300",
            "page": str(page),
            "filter": "all",
        }
        while True:
            page += 1
            deals_product_params["page"] = str(page)

            deal_products = self.boostr.get("deal_products")

            self.log.debug(f"Fetched {len(deal_products)} deal_products")

            for deal_product in deal_products:
                # TODO fix get()
                product = BoostrProduct.objects.get(
                    boostr_id=deal_product["product"]["id"]
                )
                try:
                    deal = BoostrDeal.objects.get(
                        boostr_id=deal_product["deal_id"],
                    )
                except BoostrDeal.DoesNotExist:
                    continue

                for budget in deal_product["deal_product_budgets"]:
                    BoostrDealProduct.objects.update_or_create(
                        boostr_deal=deal,
                        boostr_product=product,
                        month=budget["month"],
                        budget=budget["budget"],
                    )
                self.log.debug(
                    f'Upserted {len(deal_product["deal_product_budgets"])} months of budget for product: '
                    f"{product.boostr_id} to deal: {deal_product['product']['full_name']}"
                )

    def upsert_mediaplan(self) -> None:
        """Upsert media plan lne item details into the database"""
        # print(self.mp_data)

        for media_plan in self.mp_data:
            # exit(media_plan)
            mp = NewBoostrMediaPlan(
                media_plan_id=media_plan["id"],
                name=media_plan["deal_name"],
                boostr_deal=media_plan["deal_id"],
            )
            if media_plan["id"]:  # != 265115:
                self.mpc.add_media_plan(media_plan["deal_id"], mp)
                self.upsert_mediaplan_lineitems(mp)

        # pprint.pprint(self.mpc.media_plans)

    def upsert_mediaplan_lineitems(self, media_plan: NewBoostrMediaPlan) -> None:
        """Upsert media plan line item"""
        page = 0
        deals_params = {
            "per": "300",
            "page": str(page),
            "filter": "all",
        }

        page += 1
        deals_params["page"] = str(page)

        media_plans = self.boostr.get(
            f"media_plans/{media_plan.media_plan_id}/line_items", params=deals_params
        )
        self.log.info(f"Fetched {len(media_plans)} media plans ")

        self.append_json_file(media_plans, self.li_json_file)
        # return
        """ for li in self.li_mp_data:
            if media_plan.media_plan_id == 265115:
                pprint.pprint(li["product"]["id"])
                for month in li["line_item_monthlies"]:
                    mpli = NewBoostrDealMediaPlanLineItem(
                        media_plan_line_item_id=li["id"],
                        boostr_deal=media_plan.boostr_deal,
                        boostr_product=li["product"]["id"],
                        rate_type=li["rate_type"]["name"],
                        rate=li["rate"],
                        quantity=month["quantity"],
                        budget=month["budget"],
                        month=month["month"],
                    )
                    media_plan.add_line_item(mpli)
                    print(f"did: {mpli.boostr_deal}****")
                    bdeal = BoostrDeal.objects.get(boostr_id=mpli.boostr_deal)
                    bprod = BoostrProduct.objects.get(boostr_id=mpli.boostr_product)
                    qs = BoostrDealProduct.objects.filter(
                        month=mpli.month, boostr_deal_id=bdeal, boostr_product_id=bprod
                    )
                for obj in qs:
                    pprint.pprint((obj))
                    qs.update(
                        quantity=mpli.quantity, rate=mpli.rate, rate_type=mpli.rate_type
                    )
                      BoostrDealProduct.objects.filter
                        (month=mpli.month,boostr_deal_id=mpli.boostr_deal,boostr_product_id=mpli.boostr_product).update(
                        quantity = mpli.quantity,
                        rate = mpli.rate,
                        rate_type = mpli.rate_type
                    ) """

        # pprint.pprint(media_plan)

    def load(self):
        """Loader entry point"""
        start_time = time.time()
        # self.upsert_products()
        # self.upsert_deals()
        # self.upsert_deal_products()
        self.upsert_mediaplan()
        # self.upsert_mediaplan_lineitems()
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.log.info(f"Sync took {elapsed_time:.4f} seconds to run")


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
