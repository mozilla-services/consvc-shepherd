"""Django admin custom command for fetching and saving Deal and Product data from Boostr to Shepherd"""

import logging
import math

import requests
from django.core.management.base import BaseCommand

from consvc_shepherd.models import BoostrDeal, BoostrDealProduct, BoostrProduct

MAX_DEAL_PAGES_DEFAULT = 50


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


class BoostrLoader:
    """Wrap up interaction with the Boostr API"""

    base_url: str
    session: requests.Session
    log: logging.Logger
    max_deal_pages: int

    def __init__(
        self,
        base_url: str,
        email: str,
        password: str,
        max_deal_pages=MAX_DEAL_PAGES_DEFAULT,
    ):
        self.log = logging.getLogger("sync_boostr_data")
        self.base_url = base_url
        self.max_deal_pages = max_deal_pages
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
        while page < self.max_deal_pages:
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

                self.upsert_deal_products(boostr_deal)
                self.log.info(f"Upserted products and budgets for deal: {deal['id']}")
            # If this is the last iteration of the loop due to the max page limit, log that we stopped
            if page >= self.max_deal_pages:
                self.log.info(
                    f"Done. Stopped fetching deals after hitting max_page_limit of {page} pages."
                )

    def upsert_deal_products(self, deal: BoostrDeal) -> None:
        """Fetch the deal_products for a particular deal and store them in our DB with their monthly budgets"""
        deal_products_response = self.session.get(
            f"{self.base_url}/deals/{deal.boostr_id}/deal_products"
        )

        if deal_products_response.status_code != 200:
            raise BoostrApiError(
                f"Bad response status from /api/deals/{deal.boostr_id}/deal_products: {deal_products_response}"
            )

        deal_products = deal_products_response.json()
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

    def load(self):
        """Loader entry point"""
        self.upsert_products()
        self.upsert_deals()


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
