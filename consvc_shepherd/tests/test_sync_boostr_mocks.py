"""MockResponse utility class for testing the sync script's interactions with the Boostr API"""

import requests

from consvc_shepherd.models import BoostrDeal, BoostrDealProduct, BoostrProduct
from consvc_shepherd.tests.test_sync_boostr_mock_responses import (
    MOCK_DEAL_PRODUCTS_RESPONSE,
    MOCK_DEALS_RESPONSE,
    MOCK_PRODUCTS_RESPONSE,
)


class MockResponse:
    """Mock for returning a response, used in functions that mock requests"""

    def __init__(self, json_data: object, status_code: int):
        self.json_data = json_data
        self.status_code = status_code
        self.ok = 200 <= self.status_code < 400

    def json(self):
        """Mock json data"""
        return self.json_data


def mock_post_success(*args, **kwargs) -> MockResponse:
    """Mock successful POST requests to boostr"""
    if args[0].endswith("/user_token"):
        return MockResponse({"jwt": "i.am.jwt"}, 201)
    else:
        return MockResponse({"data": "wow", "count": 42}, 200)


def mock_post_token_fail(*args, **kwargs) -> MockResponse:
    """Mock failed POST /user_token requests to boostr"""
    return MockResponse({"uh": "oh"}, 401)


def mock_upsert_deals_exception(*args, **kwargs) -> MockResponse:
    """Mock upsert_deals exception"""
    raise Exception("upsert_deals mock raised an exception")


def mock_request_exception(*args, **kwargs):
    """Mock requests exception"""
    return requests.RequestException("Request Timeout")


def mock_get_success(*args, **kwargs) -> MockResponse:
    """Mock GET requests to boostr which handles mock responses for /products, /deals, and /deal_products"""
    if args[0].endswith("/products"):
        return MockResponse(
            MOCK_PRODUCTS_RESPONSE,
            200,
        )
    elif args[0].endswith("/deals"):
        return MockResponse(
            MOCK_DEALS_RESPONSE,
            200,
        )
    elif args[0].endswith("/deal_products"):
        return MockResponse(
            MOCK_DEAL_PRODUCTS_RESPONSE,
            200,
        )
    else:
        return MockResponse({"mock": "unknown"}, 500)


def mock_get_fail(*args, **kwargs) -> MockResponse:
    """Mock failed GET requets to boostr"""
    return MockResponse({"uh": "oh"}, 400)


def mock_too_many_requests_response(*args, **kwargs) -> requests.Response:
    """Mock 429 error returned when rate limited"""
    mock_response = requests.Response()
    mock_response.status_code = 429
    mock_response.headers["Retry-After"] = "5"
    raise requests.HTTPError(response=mock_response)


def mock_get_success_response(*args, **kwargs) -> MockResponse:
    """Mock response from sucessful get"""
    return MockResponse({"data": "success"}, 200)


def mock_update_or_create_deal(*args, **kwargs) -> tuple[BoostrDeal, bool]:
    """Mock out the DB for saving deals"""
    return (
        BoostrDeal(
            boostr_id=kwargs["boostr_id"],
            name=kwargs["defaults"]["name"],
            advertiser=kwargs["defaults"]["advertiser"],
            currency=kwargs["defaults"]["currency"],
            amount=kwargs["defaults"]["amount"],
            sales_representatives=kwargs["defaults"]["sales_representatives"],
            start_date=kwargs["defaults"]["start_date"],
            end_date=kwargs["defaults"]["end_date"],
        ),
        True,
    )


BOOSTR_PRODUCTS = {
    28256: BoostrProduct(
        boostr_id=28256,
        full_name="Firefox New Tab US (CPC)",
        country="US",
        campaign_type=BoostrProduct.CampaignType.CPC,
    ),
    212592: BoostrProduct(
        boostr_id=212592,
        full_name="Firefox 2nd Tile CA (CPM)",
        country="CA",
        campaign_type=BoostrProduct.CampaignType.CPM,
    ),
    204410: BoostrProduct(
        boostr_id=204410,
        full_name="Firefox New Tab FR (CPM)",
        country="SP",
        campaign_type=BoostrProduct.CampaignType.CPM,
    ),
}


def mock_get_product(*args, **kwargs) -> BoostrProduct:
    """Mock out retrieving a product from the DB"""
    return BOOSTR_PRODUCTS[kwargs["boostr_id"]]


def mock_update_or_create_deal_product(
    *args, **kwargs
) -> tuple[BoostrDealProduct, bool]:
    """Mock out the DB for saving deal products"""
    return (
        BoostrDealProduct(
            boostr_deal=kwargs["deal"],
            boostr_product=BoostrProduct(
                boostr_id=28256,
                full_name="Firefox New Tab US (CPC)",
                country="US",
                campaign_type=BoostrProduct.CampaignType.CPC,
            ),
            month=kwargs["month"],
            budget=kwargs["budget"],
        ),
        True,
    )
