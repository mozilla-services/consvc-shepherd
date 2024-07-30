from django.core.management.base import BaseCommand, CommandError

from dataclasses import dataclass
import logging
import math
import os
import requests

from consvc_shepherd.models import BoostrDeal, BoostrDealProduct, BoostrProduct

class Command(BaseCommand):
    help = "Run a script that calls the Boostr API and loads Deals and Products from Boostr"

    def add_arguments(self, parser):
        parser.add_argument("base_url", type=str, help="The base url for the Boostr API, eg. https://app.boostr.com/api/")
        parser.add_argument("email", type=str, help="The email for the Boostr API account to authenticate with (see 1password Ads Eng vault)")
        parser.add_argument("password", type=str, help="The password for the Boostr API account (see 1password Ads Eng vault)")

    def handle(self, *args, **options):
        loader = BoostrLoader(options["base_url"], options["email"], options["password"])
        loader.load()


class BoostrApiError(Exception):
    '''Raise this error whenever we don't get a 200 status back from boostr'''
    pass

class BoostrLoader:
    base_url: str
    headers: dict[str, str]
    log: logging.Logger

    def __init__(self, base_url: str, email: str, password: str):
        logger = logging.getLogger("sync_boostr_data")
        self.setup_config(logger, base_url, email, password)


    def authenticate(self, boostr_base_url: str, email: str, password: str, headers: dict[str, str]) -> str:
        user_token_response = requests.post(f"{boostr_base_url}/user_token", json={"auth": { "email": email, "password": password } }, headers=headers)
        if user_token_response.status_code != 201:
            raise BoostrApiError(f"Bad response status from /api/user_token: {user_token_response}")
        token = user_token_response.json()
        return token["jwt"]


    def setup_config(self, logger: logging.Logger, base_url: str, email: str, password: str) -> None:
        headers = {
            "Accept": "application/vnd.boostr.public",
            "Content-Type": "application/json"
        }
        token = self.authenticate(base_url, email, password, headers)
        headers["Authorization"] = f"Bearer {token}"
        self.base_url=base_url
        self.headers=headers
        self.log=logger


    def upsert_deals(self) -> None:
        deals_params = {
            "per": 300,
            "page": 0,
            "filter": "all",
        }
        while True:
            deals_params["page"]+=1

            deals_response = requests.get(f"{self.base_url}/deals", params=deals_params, headers=self.headers)
            if deals_response.status_code != 200:
                raise BoostrApiError(f"Bad response status from /api/deals: {deals_response}")
            deals = deals_response.json()
            self.log.info(f"Fetched {len(deals)} deals for page {deals_params['page']}")

            # Paged through all available records and are getting an empty list back
            if (len(deals) == 0):
                self.log.info(f"Done. Fetched all the deals in {deals_params['page']-1} pages")
                break

            closed_won_deals = filter(lambda d: d["stage_name"] == "Closed Won", deals)
            for deal in closed_won_deals:
                boostr_deal, ok = BoostrDeal.objects.update_or_create(
                    boostr_id=deal["id"],
                    name=deal["name"],
                    advertiser=deal["advertiser_name"],
                    currency=deal["currency"],
                    amount=math.floor(float(deal["budget"])),
                    sales_representatives=','.join(str(d["email"]) for d in deal["deal_members"]),
                    start_date=deal["start_date"],
                    end_date=deal["end_date"],
                )
                self.log.debug(f"Upserted deal: {deal['id']}")

                deal_id = deal["id"]
                deal_products_response = requests.get(f"{self.base_url}/deals/{deal_id}/deal_products", headers=self.headers)

                if deals_response.status_code != 200:
                    raise BoostrApiError(f"Bad response status from /api/deals/{deal_id}/deal_products: {deals_response}")

                deal_products = deal_products_response.json()
                self.log.debug(f"Fetched {len(deal_products)} deal_products for deal: {deal_id}")

                for deal_product in deal_products:
                    product = BoostrProduct.objects.get(boostr_id = deal_product["product"]["id"])
                    for budget in deal_product["deal_product_budgets"]:
                        deal_product_budget, ok = BoostrDealProduct.objects.update_or_create(
                            boostr_deal=boostr_deal,
                            boostr_product=product,
                            month=budget["month"],
                            budget=budget["budget"],
                        )
                    self.log.debug(f'Upserted {len(deal_product["deal_product_budgets"])} months of budget for product: {product.id} to deal: {deal_id}')
                self.log.info(f"Upserted products and budgets for deal: {deal['id']}")

    def upsert_products(self)-> None:
        products_params = {
            "per": 300,
            "page": 1,
            "filter": "all",
        }
        products_response = requests.get(f"{self.base_url}/products", params=products_params, headers=self.headers)
        products = products_response.json()
        if products_response.status_code != 200:
            raise BoostrApiError(f"Bad response status from /api/products: {products_response}")
        self.log.info(f"Fetched {(len(products))} products")

        for product in products:
            BoostrProduct.objects.update_or_create(
                boostr_id=product["id"],
                full_name=product["full_name"],
                campaign_type=get_campaign_type(product["full_name"])
            )
        self.log.info(f"Upserted {(len(products))} products")

    def load(self):
        self.upsert_products()
        self.upsert_deals()


def get_campaign_type(product_full_name: str) -> str:
    if "CPC" in product_full_name:
        return "CPC"
    if "CPM" in product_full_name:
        return "CPM"
    return "?"
