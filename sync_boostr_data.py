import django
import environ
import math
import os
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "consvc_shepherd.settings")
django.setup()

from consvc_shepherd.models import BoostrDeal, BoostrDealProduct, BoostrProduct

def sync_boostr_data()-> None:
    env = environ.Env()
    token = env("BOOSTR_JWT")

    headers = {
        "Accept": "application/json",
        "Accept": "application/vnd.boostr.public",
        "Authorization": f"Bearer {token}"
    }

    upsert_products(headers)
    upsert_deals(headers)

def upsert_deals(headers: dict[str, str]) -> None:

    deals_params = {
        "per": 300,
        "page": 0,
        "filter": "all",
    }

    while True:
        deals_params["page"]+=1

        deals_response = requests.get("https://app.boostr.com/api/deals", params=deals_params, headers=headers)
        print(f"GET /deals response status: {deals_response}")
        deals = deals_response.json()
        print(f"Got {len(deals)} deals for page {deals_params['page']}")

        # Paged through all available records and are getting an empty list back
        if (len(deals) == 0):
            print(f"Got all the deals in {deals_params['page']-1} pages")
            break

        closed_won_deals = filter(lambda d: d["stage_name"] == "Closed Won", deals)
        for deal in closed_won_deals:
            print("CLOSED WON DEAL")
            print(deal)

            boostr_deal, ok = BoostrDeal.objects.update_or_create(
                boostr_id=deal["id"],
                name=deal["name"],
                advertiser=deal["advertiser_name"],
                currency=deal["currency"],
                amount=math.floor(float(deal["budget"])),
                sales_representatives=','.join(str(d["email"]) for d in deal["deal_members"]),
                campaign_type="?",
                start_date=deal["start_date"],
                end_date=deal["end_date"],
            )
            print(f"Saved boostr deal with id {deal['id']}")
            print(boostr_deal)

            deal_id = deal["id"]
            deal_products_response = requests.get(f"https://app.boostr.com/api/deals/{deal_id}/deal_products", headers=headers)
            print(f"GET /deals/{deal_id}/deal_products response status: {deal_products_response}")

            deal_products = deal_products_response.json()
            print(f"Got {len(deal_products)} deal products for deal {deal_id}")
            print(deal_products)

            for deal_product in deal_products:
                product = BoostrProduct.objects.get(boostr_id = deal_product["product"]["id"])
                for budget in deal_product["deal_product_budgets"]:
                    deal_product, ok = BoostrDealProduct.objects.update_or_create(
                        boostr_deal=boostr_deal,
                        boostr_product=product,
                        month=budget["month"],
                        budget=budget["budget"],
                    )

            print(f"Added {len(boostr_deal.products.all())} to deal {deal_id}")



def upsert_products(headers: dict[str, str])-> None:

    products_params = {
        "per": 300,
        "page": 1,
        "filter": "all",
    }

    products_response = requests.get("https://app.boostr.com/api/products", params=products_params, headers=headers)
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
