from dataclasses import dataclass
import django
import environ
import logging
import math
import os
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "consvc_shepherd.settings")
django.setup()

from consvc_shepherd.models import BoostrDeal, BoostrDealProduct, BoostrProduct

@dataclass(frozen=True)
class BoostrSyncConfig:
    """Object to wrap up various environment configuration for the boostr snyc script"""
    base_url: str
    headers: dict[str, str]
    log: logging.Logger

class BoostrApiError(Exception):
    '''Raise this error whenever we don't get a 200 status back from boostr'''
    pass

def sync_boostr_data() -> None:
    logger = logging.getLogger("sync_boostr_data")
    try:
        config = setup_config(logger)
        upsert_products(config)
        upsert_deals(config)
    except BoostrApiError as e:
        logger.error(e)


def setup_config(logger: logging.Logger) -> BoostrSyncConfig:
    env = environ.Env()
    boostr_base_url = env("BOOSTR_BASE_URL")
    email = env("BOOSTR_EMAIL")
    password = env("BOOSTR_PASSWORD")
    headers = {
        "Accept": "application/vnd.boostr.public",
        "Content-Type": "application/json"
    }
    token = authenticate(boostr_base_url, email, password, headers)
    headers["Authorization"] = f"Bearer {token}"

    return BoostrSyncConfig(
        base_url=boostr_base_url,
        headers=headers,
        log=logger,
    )

def authenticate(boostr_base_url: str, email: str, password: str, headers: dict[str, str]) -> str:
    user_token_response = requests.post(f"{boostr_base_url}/user_token", json={"auth": { "email": email, "password": password } }, headers=headers)
    if user_token_response.status_code != 201:
        raise BoostrApiError(f"Bad response status from /api/user_token: {user_token_response}")
    token = user_token_response.json()
    return token["jwt"]

def upsert_deals(config: BoostrSyncConfig) -> None:
    deals_params = {
        "per": 300,
        "page": 0,
        "filter": "all",
    }
    while True:
        deals_params["page"]+=1

        deals_response = requests.get(f"{config.base_url}/deals", params=deals_params, headers=config.headers)
        if deals_response.status_code != 200:
            raise BoostrApiError(f"Bad response status from /api/deals: {deals_response}")
        deals = deals_response.json()
        config.log.info(f"Fetched {len(deals)} deals for page {deals_params['page']}")

        # Paged through all available records and are getting an empty list back
        if (len(deals) == 0):
            config.log.info(f"Done. Fetched all the deals in {deals_params['page']-1} pages")
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
            config.log.debug(f"Upserted deal with boostr_id: {deal['id']}")

            deal_id = deal["id"]
            deal_products_response = requests.get(f"{config.base_url}/deals/{deal_id}/deal_products", headers=config.headers)

            if deals_response.status_code != 200:
                raise BoostrApiError(f"Bad response status from /api/deals/{deal_id}/deal_products: {deals_response}")

            deal_products = deal_products_response.json()
            config.log.debug(f"Fetched {len(deal_products)} deal_products for deal: {deal_id}")

            for deal_product in deal_products:
                product = BoostrProduct.objects.get(boostr_id = deal_product["product"]["id"])
                for budget in deal_product["deal_product_budgets"]:
                    deal_product_budget, ok = BoostrDealProduct.objects.update_or_create(
                        boostr_deal=boostr_deal,
                        boostr_product=product,
                        month=budget["month"],
                        budget=budget["budget"],
                    )
                config.log.debug(f'Upserted {len(deal_product["deal_product_budgets"])} months of budget for product: {product.id} to deal: {deal_id}')

def upsert_products(config: BoostrSyncConfig)-> None:
    products_params = {
        "per": 300,
        "page": 1,
        "filter": "all",
    }
    products_response = requests.get(f"{config.base_url}/products", params=products_params, headers=config.headers)
    products = products_response.json()
    if products_response.status_code != 200:
        raise BoostrApiError(f"Bad response status from /api/products: {products_response}")
    config.log.info(f"Fetched {(len(products))} products")

    for product in products:
        BoostrProduct.objects.update_or_create(
            boostr_id=product["id"],
            full_name=product["full_name"],
            campaign_type=get_campaign_type(product["full_name"])
        )
    config.log.info(f"Upserted {(len(products))} products")


def get_campaign_type(product_full_name: str) -> str:
    if "CPC" in product_full_name:
        return "CPC"
    if "CPM" in product_full_name:
        return "CPM"
    return "?"


if __name__ == "__main__":
    sync_boostr_data()
