from dataclasses import dataclass
from datetime import datetime
import time
import django
import environ
import logging
import math
import os
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "consvc_shepherd.settings")
django.setup()

from consvc_shepherd.models import (
    BoostrDeal,
    BoostrDealMediaPlanLineItem,
    BoostrDealProduct,
    BoostrProduct,
    BoostrDealMediaPlan,
)


@dataclass(frozen=True)
class BoostrSyncConfig:
    """Object to wrap up various environment configuration for the boostr snyc script"""

    base_url: str
    headers: dict[str, str]
    log: logging.Logger


class BoostrApiError(Exception):
    """Raise this error whenever we don't get a 200 status back from boostr"""

    pass


def sync_boostr_data() -> None:
    logger = logging.getLogger("sync_boostr_data")
    start_time = time.time()
    try:
        config = setup_config(logger)
        # upsert_products(config)
        # upsert_deals(config)
        upsert_media_plans(config)
        # upsert_deal_products(config)
    except BoostrApiError as e:
        logger.error(e)
    end_time = time.time()
    elapsed_time = start_time - end_time
    print(f"Sync took {elapsed_time:.4f} seconds to run")


def setup_config(logger: logging.Logger) -> BoostrSyncConfig:
    env = environ.Env()
    boostr_base_url = env("BOOSTR_BASE_URL")
    email = env("BOOSTR_EMAIL")
    password = env("BOOSTR_PASSWORD")
    headers = {
        "Accept": "application/vnd.boostr.public",
        "Content-Type": "application/json",
    }
    token = authenticate(boostr_base_url, email, password, headers)
    headers["Authorization"] = f"Bearer {token}"

    return BoostrSyncConfig(
        base_url=boostr_base_url,
        headers=headers,
        log=logger,
    )


def authenticate(
    boostr_base_url: str, email: str, password: str, headers: dict[str, str]
) -> str:
    user_token_response = requests.post(
        f"{boostr_base_url}/user_token",
        json={"auth": {"email": email, "password": password}},
        headers=headers,
    )
    if user_token_response.status_code != 201:
        raise BoostrApiError(
            f"Bad response status from /api/user_token: {user_token_response}"
        )
    token = user_token_response.json()
    return token["jwt"]


def upsert_deals(config: BoostrSyncConfig) -> None:
    deals_params = {
        "per": 300,
        "page": 0,
        "filter": "all",
    }
    while True:
        deals_params["page"] += 1

        deals_response = requests.get(
            f"{config.base_url}/deals", params=deals_params, headers=config.headers
        )
        if deals_response.status_code != 200:
            raise BoostrApiError(
                f"Bad response status from /api/deals: {deals_response}"
            )
        deals = deals_response.json()
        config.log.info(f"Fetched {len(deals)} deals for page {deals_params['page']}")

        # Paged through all available records and are getting an empty list back
        if len(deals) == 0:
            config.log.info(
                f"Done. Fetched all the deals in {deals_params['page']-1} pages"
            )
            break

        closed_won_deals = filter(lambda d: d["stage_name"] == "Closed Won", deals)
        for deal in closed_won_deals:
            boostr_deal, ok = BoostrDeal.objects.update_or_create(
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
            config.log.info(f"Upserted deal with boostr_id: {deal['id']}")


def upsert_products(config: BoostrSyncConfig) -> None:
    products_params = {
        "per": 300,
        "page": 1,
        "filter": "all",
    }
    products_response = requests.get(
        f"{config.base_url}/products", params=products_params, headers=config.headers
    )
    products = products_response.json()
    if products_response.status_code != 200:
        raise BoostrApiError(
            f"Bad response status from /api/products: {products_response}"
        )
    config.log.info(f"Fetched {(len(products))} products")

    for product in products:
        BoostrProduct.objects.update_or_create(
            boostr_id=product["id"],
            full_name=product["full_name"],
            campaign_type=get_campaign_type(product["full_name"]),
        )
    config.log.info(f"Upserted {(len(products))} products")


def upsert_media_plans(config: BoostrSyncConfig) -> None:
    media_plans_params = {
        "per": 300,
        "page": 0,
        "filter": "all",
    }
    # TODO Add the paging loop
    while True:
        media_plans_params["page"] += 1
        media_plans_response = requests.get(
            f"{config.base_url}/media_plans",
            params=media_plans_params,
            headers=config.headers,
        )
        media_plans = media_plans_response.json()
        if media_plans_response.status_code != 200:
            raise BoostrApiError(
                f"Bad response status from /media_plans {media_plans_response}"
            )
        config.log.info(f"Fetched {(len(media_plans))} media plans")
        # Paged through all available records and are getting an empty list back
        if len(media_plans) == 0:
            config.log.info(
                f"Done. Fetched all themedia plans in {media_plans_params['page']-1} pages"
            )
            break

        for media_plan in media_plans:
            #print(f"Getting media plan id: {media_plan}")
            # exit()
            # continue
            try:
                boostr_deal_instance = BoostrDeal.objects.get(
                    boostr_id=media_plan["deal_id"]
                )
            except BoostrDeal.DoesNotExist:
                continue

            BoostrDealMediaPlan.objects.update_or_create(
                media_plan_id=media_plan["id"],
                name=media_plan["name"],
                boostr_deal=boostr_deal_instance,
                # defaults={"boostr_deal": boostr_deal_instance},
                # boostr_deal=media_plan["deal_id"],
            )

            upsert_media_plan_line_items(config, media_plan["id"])
        config.log.info(f"Upserted {(len(media_plan))} media plans")


def upsert_media_plan_line_items(config: BoostrSyncConfig, media_plan_id: int) -> None:
    media_plan_line_items_params = {
        "per": 300,
        "page": 1,
        "filter": "all",
    }
    # TODO Add the paging loop
    #media_plan_line_items_params["page"] += 1
    print(f"{config.base_url}media_plans/{media_plan_id}/line_items")
    media_plan_items_response = requests.get(
        f"{config.base_url}media_plans/{media_plan_id}/line_items",
        params=media_plan_line_items_params,
        headers=config.headers,
    )
    media_plan_line_items = media_plan_items_response.json()
    if media_plan_items_response.status_code != 200:
        raise BoostrApiError(
            f"Bad response status from /media_plans/line_itmes {media_plan_items_response}"
        )
    config.log.info(f"Fetched {(len(media_plan_line_items))} media plan line items")
    # Paged through all available records and are getting an empty list back
    if len(media_plan_line_items) == 0:
        config.log.info(
            f"Done. Fetched all themedia plans in {media_plan_line_items_params['page']-1} pages"
        )
        return

    for media_plan_line_item in media_plan_line_items:
        #print(f"Getting media plan id: {media_plan_line_item}")
        try:
            media_plan_instance = BoostrDealMediaPlan.objects.get(
                media_plan_id=media_plan_id
            )
        except BoostrDealMediaPlan.DoesNotExist:
            print("Media plan not found")
            return

        BoostrDealMediaPlanLineItem.objects.update_or_create(
            media_plan_line_item_id=media_plan_line_item["id"],
            media_plan_id=media_plan_instance,
            rate_type=media_plan_line_item["rate_type"]["name"],
            rate=media_plan_line_item["rate"],
            quantity=media_plan_line_item["quantity"],
            budget=media_plan_line_item["budget"],
        )
        print(f"Media plan li {media_plan_line_item['id']} inserted")
    config.log.info(f"Upserted {(len(media_plan_line_item))} media plans")


def upsert_deal_products(config: BoostrSyncConfig) -> None:
    deal_products_params = {
        "per": 300,
        "page": 0,
        "filter": "all",
    }
    while True:
        deal_products_params["page"] += 1
        deal_products_response = requests.get(
            f"{config.base_url}/deal_products",
            params=deal_products_params,
            headers=config.headers,
        )
        deal_products = deal_products_response.json()
        if deal_products_response.status_code != 200:
            raise BoostrApiError(
                f"Bad response status from /deal_products {deal_products_response}"
            )
            # Paged through all available records and are getting an empty list back
        if len(deal_products) == 0:
            config.log.info(
                f"Done. Fetched all the deal products in {deal_products_params['page']-1} pages"
            )
            break

        config.log.info(f"Fetched {(len(deal_products))} media plans")

        for deal_product in deal_products:
            print(f"boostr deal id:{deal_product['deal_id']}")
            # exit()
            try:
                product = BoostrProduct.objects.get(
                    boostr_id=deal_product["product"]["id"]
                )
            except BoostrProduct.DoesNotExist:
                continue

            try:
                deal = BoostrDeal.objects.get(boostr_id=deal_product["deal_id"])
            except BoostrDeal.DoesNotExist:
                continue

            for budget in deal_product["deal_product_budgets"]:
                deal_product_budget, ok = BoostrDealProduct.objects.update_or_create(
                    boostr_deal=deal,
                    boostr_product=product,
                    month=datetime.strptime(budget["month"], "%Y-%m").date(),
                    budget=budget["budget"],
                )
                config.log.info(
                    f"Inserted a deal_products for deal: {deal.boostr_id} product: {product.boostr_id}"
                )
            config.log.debug(
                f'Upserted {len(deal_product["deal_product_budgets"])} months of budget for product: {product.id} to deal: {deal.boostr_id}'
            )


def get_campaign_type(product_full_name: str) -> str:
    if "CPC" in product_full_name:
        return "CPC"
    if "CPM" in product_full_name:
        return "CPM"
    return "?"


if __name__ == "__main__":
    sync_boostr_data()
