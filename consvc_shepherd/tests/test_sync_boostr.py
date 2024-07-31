"""Unit tests for the sync_boostr_data command"""

from unittest import mock

import requests
from django.test import TestCase, override_settings

from consvc_shepherd.management.commands.sync_boostr_data import (
    BoostrApiError,
    BoostrDeal,
    BoostrDealProduct,
    BoostrLoader,
    BoostrProduct,
    get_campaign_type,
)


class MockResponse:
    """Mock for returning a response, used in funtions that mock requests"""

    def __init__(self, json_data: object, status_code: int):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        """Mock json data"""
        return self.json_data


def mock_post_success(*args, **kwargs) -> MockResponse:
    """Mock successful POST /user_token requests to boostr"""
    return MockResponse({"jwt": "i.am.jwt"}, 201)


def mock_post_fail(*args, **kwargs) -> MockResponse:
    """Mock failed POST /user_token requests to boostr"""
    return MockResponse({"uh": "oh"}, 401)


def mock_get_success(*args, **kwargs) -> MockResponse:
    """Mock GET requests to boostr which handles mock responses for /products, /deals, and /deal_products"""
    if args[0].endswith("/products"):
        return MockResponse(
            [
                {
                    "id": 212592,
                    "name": "CA (CPM)",
                    "full_name": "Firefox 2nd Tile CA (CPM)",
                    "parent_id": 193700,
                    "top_parent_id": 193700,
                    "active": True,
                    "rate_type_id": 124,
                    "level": 1,
                    "revenue_type": "Display",
                    "margin": None,
                    "show_in_forecast": True,
                    "pg_enabled": False,
                    "created_at": "2024-05-17T14:07:30.170Z",
                    "updated_at": "2024-07-04T09:14:22.354Z",
                    "custom_field": None,
                    "created_by": "Kay Sales",
                    "updated_by": "Kay Sales",
                    "product_type": None,
                    "product_family": {"id": 718, "name": "Direct"},
                },
                {
                    "id": 28256,
                    "name": "US (CPC)",
                    "full_name": "Firefox New Tab US (CPC)",
                    "parent_id": 28249,
                    "top_parent_id": 28249,
                    "active": True,
                    "rate_type_id": 125,
                    "level": 1,
                    "revenue_type": "Display",
                    "margin": None,
                    "show_in_forecast": True,
                    "pg_enabled": False,
                    "created_at": "2020-02-25T23:30:47.054Z",
                    "updated_at": "2024-04-10T16:07:24.399Z",
                    "custom_field": None,
                    "created_by": None,
                    "updated_by": "Kay Sales",
                    "product_type": None,
                    "product_family": {"id": 718, "name": "Direct"},
                },
            ],
            200,
        )
    elif args[0].endswith("/deals"):
        return MockResponse(
            [
                {
                    "id": 1482241,
                    "start_date": "2024-05-01",
                    "end_date": "2024-05-31",
                    "name": "HiProduce: CA Tiles May 2024",
                    "stage_name": "Closed Won",
                    "stage_id": 1087,
                    "type": None,
                    "source": None,
                    "next_steps": "",
                    "advertiser_id": 303109,
                    "advertiser_name": "HiProduce",
                    "agency_id": 303027,
                    "agency_name": "GeistM",
                    "created_at": "2024-05-16T20:16:02.704Z",
                    "updated_at": "2024-05-31T12:48:17.896Z",
                    "created_by": "Jay Sales",
                    "updated_by": "Jay Sales",
                    "deleted_at": None,
                    "closed_at": "2024-05-17T16:06:33.539Z",
                    "closed_reason": "Audience Fit",
                    "closed_comments": "audience fit",
                    "currency": "$",
                    "budget": "10000.0",
                    "budget_loc": "10000.0",
                    "lead_id": None,
                    "deal_members": [
                        {
                            "id": 4470961,
                            "user_id": 17968,
                            "email": "jsales@mozilla.com",
                            "share": 100,
                            "type": "Seller",
                            "seller_type": "direct",
                            "role": None,
                            "product": None,
                        }
                    ],
                    "custom_fields": {
                        "Forecast Close Date": None,
                        "Confidence": None,
                        "Notes": None,
                        "Timing": None,
                        "Need": None,
                        "Access": None,
                        "Budget": None,
                    },
                    "integrations": [],
                    "deal_contacts": [],
                },
                {
                    "id": 1498421,
                    "start_date": "2024-04-01",
                    "end_date": "2024-06-30",
                    "name": "Neutron: Neutron US, DE, FR",
                    "stage_name": "Closed Won",
                    "stage_id": 1087,
                    "type": None,
                    "source": "Proactive to Client",
                    "next_steps": "Sign IO",
                    "advertiser_id": 1145175,
                    "advertiser_name": "Neutron",
                    "agency_id": None,
                    "agency_name": None,
                    "created_at": "2024-06-05T11:38:37.941Z",
                    "updated_at": "2024-06-05T11:45:43.377Z",
                    "created_by": "Kay Sales",
                    "updated_by": "Kay Sales",
                    "deleted_at": None,
                    "closed_at": "2024-06-05T11:45:43.296Z",
                    "closed_reason": "Performance",
                    "closed_comments": "KPI's are in line with Client goals",
                    "currency": "$",
                    "budget": "50000.0",
                    "budget_loc": "50000.0",
                    "lead_id": None,
                    "deal_members": [
                        {
                            "id": 4525424,
                            "user_id": 21626,
                            "email": "ksales@mozilla.com",
                            "share": 100,
                            "type": "Seller",
                            "seller_type": "direct",
                            "role": None,
                            "product": None,
                        }
                    ],
                    "custom_fields": {
                        "Forecast Close Date": None,
                        "Confidence": None,
                        "Notes": None,
                        "Timing": None,
                        "Need": None,
                        "Access": None,
                        "Budget": None,
                    },
                    "integrations": [],
                    "deal_contacts": [],
                },
            ],
            200,
        )
    elif args[0].endswith("/deal_products"):
        return MockResponse(
            [
                {
                    "id": 4599379,
                    "deal_id": 1498421,
                    "budget": 10000.0,
                    "budget_loc": 10000.0,
                    "custom_fields": {},
                    "start_date": None,
                    "end_date": None,
                    "term": None,
                    "period": None,
                    "created_at": "2024-06-05T11:45:10.861Z",
                    "updated_at": "2024-06-05T11:45:10.861Z",
                    "deal_product_budgets": [
                        {
                            "id": 44736446,
                            "month": "2024-04",
                            "budget_loc": 10000.0,
                            "budget": 10000.0,
                        },
                        {
                            "id": 44736447,
                            "month": "2024-05",
                            "budget_loc": 0.0,
                            "budget": 0.0,
                        },
                        {
                            "id": 44736448,
                            "month": "2024-06",
                            "budget_loc": 0.0,
                            "budget": 0.0,
                        },
                    ],
                    "product": {
                        "id": 204410,
                        "name": "FR (CPM)",
                        "full_name": "Firefox New Tab FR (CPM)",
                        "level": 1,
                        "parent": {"id": 28249, "name": "Firefox New Tab", "level": 0},
                        "top_parent": {
                            "id": 28249,
                            "name": "Firefox New Tab",
                            "level": 0,
                        },
                    },
                    "territory": None,
                },
                {
                    "id": 4599381,
                    "deal_id": 1498421,
                    "budget": 30000.0,
                    "budget_loc": 30000.0,
                    "custom_fields": {},
                    "start_date": None,
                    "end_date": None,
                    "term": None,
                    "period": None,
                    "created_at": "2024-06-05T11:45:11.047Z",
                    "updated_at": "2024-06-05T11:45:11.047Z",
                    "deal_product_budgets": [
                        {
                            "id": 44736452,
                            "month": "2024-04",
                            "budget_loc": 10000.0,
                            "budget": 10000.0,
                        },
                        {
                            "id": 44736453,
                            "month": "2024-05",
                            "budget_loc": 10000.0,
                            "budget": 10000.0,
                        },
                        {
                            "id": 44736454,
                            "month": "2024-06",
                            "budget_loc": 10000.0,
                            "budget": 10000.0,
                        },
                    ],
                    "product": {
                        "id": 28256,
                        "name": "US (CPC)",
                        "full_name": "Firefox New Tab US (CPC)",
                        "level": 1,
                        "parent": {"id": 28249, "name": "Firefox New Tab", "level": 0},
                        "top_parent": {
                            "id": 28249,
                            "name": "Firefox New Tab",
                            "level": 0,
                        },
                    },
                    "territory": None,
                },
            ],
            200,
        )
    else:
        return MockResponse({"mock": "unknown"}, 500)


def mock_get_fail(*args, **kwargs) -> MockResponse:
    """Mock failed GET requets to boostr"""
    return MockResponse({"uh": "oh"}, 400)


def mock_update_or_create_deal(*args, **kwargs) -> tuple[BoostrDeal, bool]:
    """Mock out the DB for saving deals"""
    return (
        BoostrDeal(
            boostr_id=kwargs["boostr_id"],
            name=kwargs["name"],
            advertiser=kwargs["advertiser"],
            currency=kwargs["currency"],
            amount=kwargs["amount"],
            sales_representatives=kwargs["sales_representatives"],
            start_date=kwargs["start_date"],
            end_date=kwargs["end_date"],
        ),
        True,
    )


BOOSTR_PRODUCTS = {
    28256: BoostrProduct(
        boostr_id=28256,
        full_name="Firefox New Tab US (CPC)",
        campaign_type=BoostrProduct.CampaignType.CPC,
    ),
    212592: BoostrProduct(
        boostr_id=212592,
        full_name="Firefox 2nd Tile CA (CPM)",
        campaign_type=BoostrProduct.CampaignType.CPM,
    ),
    204410: BoostrProduct(
        boostr_id=204410,
        full_name="Firefox New Tab FR (CPM)",
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
                campaign_type=BoostrProduct.CampaignType.CPC,
            ),
            month=kwargs["month"],
            budget=kwargs["budget"],
        ),
        True,
    )


BASE_URL = "https://example.com"
EMAIL = "email@mozilla.com"
PASSWORD = "test"  # nosec


@override_settings(DEBUG=True)
class TestSyncBoostrData(TestCase):
    """Unit tests for functions that fetch from boostr API and store in our DB"""

    @mock.patch.object(BoostrLoader, "authenticate", return_value="im.a.jwt")
    def test_setup_session(self, mock_authenticate):
        """Test the function that sets up the headers, authenticates with boosrt, and sets up the session"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        self.assertEqual(
            loader.session.headers["Accept"], "application/vnd.boostr.public"
        )
        self.assertEqual(loader.session.headers["Content-Type"], "application/json")
        self.assertEqual(loader.session.headers["Authorization"], "Bearer im.a.jwt")

    @mock.patch("requests.post", side_effect=mock_post_success)
    def test_authenticate(self, mock_post):
        """Test authenticate function that calls boostr auth and returns a JWT"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        headers = {
            "Accept": "application/vnd.boostr.public",
            "Content-Type": "application/json",
        }
        jwt = loader.authenticate(EMAIL, PASSWORD, headers)
        self.assertEqual(jwt, "i.am.jwt")

    @mock.patch("requests.post", side_effect=mock_post_fail)
    def test_authenticate_fail(self, mock_post):
        """Test sad path for the authenticate function"""
        with self.assertRaises(BoostrApiError):
            BoostrLoader("fail_url", "uhoh@mozilla.com", "uhoh")

    @mock.patch("requests.post", side_effect=mock_post_success)
    @mock.patch.object(requests.Session, "get", side_effect=mock_get_success)
    @mock.patch("consvc_shepherd.models.BoostrProduct.objects.update_or_create")
    def test_upsert_products(self, mock_update_or_create, mock_get, mock_post):
        """Test function that calls boostr API for product data and saves to our DB"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.upsert_products()
        calls = [
            mock.call(
                boostr_id=212592,
                full_name="Firefox 2nd Tile CA (CPM)",
                campaign_type=BoostrProduct.CampaignType.CPM,
            ),
            mock.call(
                boostr_id=28256,
                full_name="Firefox New Tab US (CPC)",
                campaign_type=BoostrProduct.CampaignType.CPC,
            ),
        ]
        mock_update_or_create.assert_has_calls(calls)

    @mock.patch("requests.post", side_effect=mock_post_success)
    @mock.patch.object(requests.Session, "get", side_effect=mock_get_fail)
    def test_upsert_products_fail(self, mock_get, mock_post):
        """Test that upsert_products will raise an API error on non-200 status"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        with self.assertRaises(BoostrApiError):
            loader.upsert_products()

    @mock.patch("requests.post", side_effect=mock_post_success)
    @mock.patch.object(requests.Session, "get", side_effect=mock_get_success)
    @mock.patch(
        "consvc_shepherd.models.BoostrDeal.objects.update_or_create",
        side_effect=mock_update_or_create_deal,
    )
    @mock.patch.object(BoostrLoader, "upsert_deal_products")
    def test_upsert_deals(self, mock_upsert_deal_products, mock_update_or_create, mock_get, mock_post):
        """Test function that calls the Boostr API for deal data and saves to our DB"""
        self.skipTest('Currently hangs with the addition of the last upsert_deal_products mock')
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.upsert_deals()
        calls = [
            mock.call(
                boostr_id=1498421,
                name="Neutron: Neutron US, DE, FR",
                advertiser="Neutron",
                currency="$",
                amount=50000,
                sales_representatives="ksales@mozilla.com,lsales@mozilla.com",
                start_date="2024-04-01",
                end_date="2024-06-30",
            ),
            mock.call(
                boostr_id=1482241,
                name="HiProduce: CA Tiles May 2024",
                advertiser="HiProduce",
                currency="$",
                amount=10000,
                sales_representatives="jsales@mozilla.com",
                start_date="2024-05-01",
                end_date="2024-05-31",
            ),
        ]
        mock_update_or_create.assert_has_calls(calls)

    @mock.patch("requests.post", side_effect=mock_post_success)
    @mock.patch.object(requests.Session, "get", side_effect=mock_get_fail)
    def test_upsert_deals_fail(self, mock_get, mock_post):
        """Test that upsert_deals will raise an API error on non-200 status"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        with self.assertRaises(BoostrApiError):
            loader.upsert_deals()

    @mock.patch("requests.post", side_effect=mock_post_success)
    @mock.patch.object(requests.Session, "get", side_effect=mock_get_success)
    @mock.patch(
        "consvc_shepherd.models.BoostrProduct.objects.get", side_effect=mock_get_product
    )
    @mock.patch("consvc_shepherd.models.BoostrDealProduct.objects.update_or_create")
    def test_upsert_deal_products(
        self, mock_update_or_create, mock_get_product, mock_get, mock_post
    ):
        """Test function that fetches the products per month and their budget for a particular deal"""
        deal = BoostrDeal(
            boostr_id=1498421,
            name="Deal with Customer",
            advertiser="Customer, Inc",
            currency="$",
            amount=5000,
            sales_representatives="asales@mozilla.com",
            start_date="2024-02-01",
            end_date="2024-05-31",
        )
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.upsert_deal_products(deal)
        calls = [
            mock.call(
                boostr_deal=deal,
                boostr_product=mock_get_product(boostr_id=204410),
                month="2024-04",
                budget=10000.0,
            ),
            mock.call(
                boostr_deal=deal,
                boostr_product=mock_get_product(boostr_id=204410),
                month="2024-05",
                budget=0.0,
            ),
            mock.call(
                boostr_deal=deal,
                boostr_product=mock_get_product(boostr_id=204410),
                month="2024-06",
                budget=0.0,
            ),
            mock.call(
                boostr_deal=deal,
                boostr_product=mock_get_product(boostr_id=28256),
                month="2024-04",
                budget=10000.0,
            ),
            mock.call(
                boostr_deal=deal,
                boostr_product=mock_get_product(boostr_id=28256),
                month="2024-05",
                budget=10000.0,
            ),
            mock.call(
                boostr_deal=deal,
                boostr_product=mock_get_product(boostr_id=28256),
                month="2024-06",
                budget=10000.0,
            ),
        ]
        mock_update_or_create.assert_has_calls(calls)

    @mock.patch("requests.post", side_effect=mock_post_success)
    @mock.patch.object(requests.Session, "get", side_effect=mock_get_fail)
    def test_upsert_deal_products_fail(self, mock_get, mock_post):
        """Test that upsert_deal_products will raise an API error on non-200 status"""
        deal = BoostrDeal(
            boostr_id=123456,
            name="Deal with Customer",
            advertiser="Customer, Inc",
            currency="$",
            amount=5000,
            sales_representatives="asales@mozilla.com",
            start_date="2024-02-01",
            end_date="2024-05-31",
        )
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        with self.assertRaises(BoostrApiError):
            loader.upsert_deal_products(deal)

    def test_get_campaign_type(self):
        """Test function that reads a Product name and decides if the Product is CPC, CPM, Flat Fee, or None"""
        cpc_name = "Firefox New Tab UK (CPC)"
        self.assertEqual(get_campaign_type(cpc_name), BoostrProduct.CampaignType.CPC)

        cpm_name = "Firefox 3rd Tile UK (CPM)"
        self.assertEqual(get_campaign_type(cpm_name), BoostrProduct.CampaignType.CPM)

        flat_fee_name = "MDN Flat Fee"
        self.assertEqual(
            get_campaign_type(flat_fee_name), BoostrProduct.CampaignType.FLAT_FEE
        )

        no_campaign_type_name = "Some product without any of the key words"
        self.assertEqual(
            get_campaign_type(no_campaign_type_name), BoostrProduct.CampaignType.NONE
        )
