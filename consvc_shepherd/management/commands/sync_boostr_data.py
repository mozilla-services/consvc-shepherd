"""Django admin custom command for fetching and saving Deal and Product data from Boostr to Shepherd"""

import json
import logging
import math
import os
import time
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List

import environ
import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from consvc_shepherd.models import BoostrDeal, BoostrDealProduct, BoostrProduct

env = environ.Env()


@dataclass(frozen=True)
class NewBoostrDealMediaPlanLineItem:
    """TODO"""

    media_plan_line_item_id: int
    media_plan_id: int
    boostr_product: int
    rate_type: str
    rate: Decimal
    quantity: int
    budget: Decimal

    def __str__(self) -> str:
        return f"{self.media_plan_id}"


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
        if line_item.media_plan_line_item_id not in self.line_items:
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

    def handle(self, *args, **options):
        """Handle running the command"""
        loader = BoostrLoader(
            options["base_url"], options["email"], options["password"]
        )
        loader.load()


class BoostrApiError(Exception):
    """Raise this error whenever we don't get a 200 status back from boostr"""

    pass


class BoostrLoader:
    """Wrap up interaction with the Boostr API"""

    base_url: str
    session: requests.Session
    log: logging.Logger

    line_items: Dict[int, NewBoostrDealMediaPlanLineItem]
    current_dir = os.path.dirname(__file__)
    json_file = os.path.join(current_dir, "mediaplans.json")

    with open(json_file, "r") as file:
        mp_data = json.load(file)
    # print(mp_data)

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
        token = self.authenticate(email, password, headers)
        headers["Authorization"] = f"Bearer {token}"
        s = requests.Session()
        s.headers.update(headers)
        self.session = s

    def authenticate(self, email: str, password: str, headers: dict[str, str]) -> str:
        """Authenticate with the Boostr API and return jwt"""
        if settings.BOOSTR_AUTH_BYPASS:
            # if we are local, bypass auth to avoid rate limits
            return str(env("BOOSTR_JWT"))
        user_token_response = requests.post(
            f"{self.base_url}/user_token",
            json={"auth": {"email": email, "password": password}},
            headers=headers,
            timeout=15,
        )
        if user_token_response.status_code != 201:

            raise BoostrApiError(
                f"Bad response status from /api/user_token: {user_token_response}"
            )
        token = user_token_response.json()
        return str(token["jwt"])

    def upsert_products(self) -> None:
        """Fetch all Boostr products and upsert them to Shepherd DB"""
        products_params = {
            "per": "300",
            "page": "1",
            "filter": "all",
        }
        products_response = self.session.get(
            f"{self.base_url}/products", params=products_params
        )
        if products_response.status_code != 200:
            raise BoostrApiError(
                f"Bad response status from /api/products: {products_response}"
            )
        products = products_response.json()
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
        while True:
            page += 1
            deals_params["page"] = str(page)

            deals_response = self.session.get(
                f"{self.base_url}/deals", params=deals_params
            )

            if deals_response.status_code != 200:
                raise BoostrApiError(
                    f"Bad response status from /api/deals: {deals_response}"
                )
            deals = deals_response.json()
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

            deal_products_response = self.session.get(
                f"{self.base_url}/deal_products", params=deals_product_params
            )

            if deal_products_response.status_code != 200:
                raise BoostrApiError(
                    f"Bad response status from /api/deal_products: \
                    {deal_products_response.reason} {deals_product_params}"
                )

            deal_products = deal_products_response.json()

            # Paged through all available records and are getting an empty list back
            if len(deal_products) == 0:
                total_pages = int(deals_product_params["page"]) - 1
                self.log.info(
                    f"Done. Fetched all deal products plans in {total_pages} pages"
                )
                break

            self.log.debug(f"Fetched {len(deal_products)} deal_products")

            for deal_product in deal_products:
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
        mpc = MediaPlanCollection()

        for media_plan in self.mp_data:
            # exit(media_plan)
            mp = NewBoostrMediaPlan(
                media_plan_id=media_plan["id"],
                name=media_plan["deal_name"],
                boostr_deal=media_plan["deal_id"],
            )
            mpc.add_media_plan(media_plan["deal_id"], mp)
        import pprint

        pprint.pprint(mpc.media_plans)

    def upsert_mediaplan_lineitems(self) -> None:
        """Upsert media plan line item"""
        pass

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
