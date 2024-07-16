import django
import environ
import os
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "consvc_shepherd.settings")
django.setup()

from consvc_shepherd.models import BoostrDeal, BoostrProduct

def sync_boostr_data()-> None:
    env = environ.Env()
    bearer_token = env("BOOSTR_JWT")

    # upsert_deals(bearer_token)
    upsert_products(bearer_token)
    # upsert_deal_products(bearer_token)

def upsert_deals(token: str) -> None:

    boostr_headers = {
        # "Accept": "application/json",
        # "Accept": "application/vnd.boostr.public",
        "Authorization": f"Bearer {token}"
    }

    deals_params = {
        "per": 300,
        "page": 0,
        "filter": "all",
    }

    while True:
        deals_params["page"]+=1

        deals_response = requests.get("https://app.boostr.com/api/deals", params=deals_params, headers=boostr_headers)
        print(f"GET /deals resposne status: {deals_response}")
        deals = deals_response.json()
        print(f"Got {len(deals)} deals for page {deals_params['page']}")

        # Paged through all available records and are getting an empty list back
        if (len(deals) == 0):
            print(f"Got all the deals in {deals_params['page']-1} pages")
            break

        closed_won_deals = filter(lambda d: d["stage"]["name"] == "Closed Won", deals)
        for deal in closed_won_deals:
            print("CLOSED WON DEAL")
            print(deal)
            boostr_deal = BoostrDeal.objects.update_or_create(
                boostr_id=deal["id"],
                name=deal["name"],
                advertiser=deal["advertiser"]["name"],
                currency=deal["curr_cd"],
                amount=deal["budget"],
                sales_representatives=','.join(str(d["name"]) for d in deal["deal_members"]),
                campaign_type="?",
                start_date=deal["start_date"],
                end_date=deal["end_date"],
            )

def upsert_products(token: str)-> None:
    boostr_headers = {
        "Accept": "application/json",
        "Accept": "application/vnd.boostr.public",
        "Authorization": f"Bearer {token}"
    }

    products_params = {
        "per": 300,
        "page": 1,
        "filter": "all",
    }

    products_response = requests.get(f"https://app.boostr.com/api/products", params=products_params, headers=boostr_headers)
    print(products_response.text)
    products = products_response.json()
    print(len(products))

    for product in products:
        print("PRODUCT")
        print(product)
        BoostrProduct.objects.update_or_create(
            boostr_id=product["id"],
            full_name=product["full_name"],
            campaign_type=get_campaign_type(product["full_name"])
        )

def get_campaign_type(product_full_name: str) -> str:
    if "CPC" in product_full_name:
        return "CPC"
    if "CPM" in product_full_name:
        return "CPM"
    return "?"


sync_boostr_data()
