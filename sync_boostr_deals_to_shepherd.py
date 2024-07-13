import django
import os
import requests

from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "consvc_shepherd.settings")
django.setup()

from consvc_shepherd.models import BoostrDeal, BoostrProduct

def populate_deals() -> None:
    boostr_headers = {
        "Authorization": "Bearer shh"
    }

    deals_params = {
        # These params seem pretty cool but don't do anything?
        # "sort_by": "closed_at",
        # "order_by": "DESC",
        # "closed_at": "2022-01-01",
        # "closed_at_condition": ">=",
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
            boostr_deal = BoostrDeal.objects.create(
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

            # deal_products_params = {
            #     "created_at_start": "2022-01-01",
            #     "filter": "all",
            #     "sort_by": "created_at DESC",
            #     "page": 1,
            #     "per": 300
            # }

            # products_response = requests.get(f"https://app.boostr.com/api/deals/{deal['id']}/deal_products", params=deal_products_params, headers=boostr_headers)
            # print(f"https://app.boostr.com/api/deals/{deal['id']}/deal_products")
            # print(products_response.text)
            # products = products_response.json()
            # print(len(products))

            # for product in products:
            #     print("PRODUCT")
            #     print(product)
            #     BoostrProduct.objects.create(
            #         boostr_id=product["id"],
            #         name=product["product"]["name"],
            #         campaign_type="?",
            #         country_code="?",
            #         start_date=product["start_date"],
            #         end_date=product["end_date"],
            #         deal=boostr_deal,
            #     )

populate_deals()
