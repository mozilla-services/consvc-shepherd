"""Unit tests for the sync_boostr_data command"""

from decimal import Decimal
from unittest import mock

from django.test import TestCase, override_settings
from more_itertools import side_effect

from consvc_shepherd.management.commands.sync_boostr_data import (
    BoostrApi,
    BoostrApiError,
    BoostrDeal,
    BoostrDealMediaPlanLineItem,
    BoostrDealProduct,
    BoostrLoader,
    BoostrMediaPlan,
    BoostrProduct,
    get_campaign_type,
)


class MockResponse:
    """Mock for returning a response, used in funtions that mock requests"""

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
    elif args[0].endswith("/media_plans"):
        return MockResponse(
            [
                {
                    "id": 265115,
                    "deal_id": 1447175,
                    "deal_name": "ATN: Q2 2024 Firefox Campaigns",                    
                },
                {
                    "id": 271925,
                    "deal_id": 1412834,
                    "deal_name": "Fintie: Fintie May - July 2024 Test",                    
                },
            ],
            200,
        )
    elif args[0].endswith("/line_items"):
        return MockResponse(
            [
                {
                    "id": 28254111111,
                    "available_units": None,
                    "total_capacity": None,
                    "name": "Firefox New Tab New Tab US (CPM)",
                    "start_date": "2024-04-01",
                    "end_date": "2024-06-30",
                    "budget": "418500.0",
                    "budget_loc": "418500.0",
                    "rate": "0.93",
                    "rate_loc": "0.93",
                    "quantity": 450000000,
                    "is_added_value": False,
                    "est_cost": "0.0",
                    "est_cost_loc": "0.0",
                    "margin": 100,
                    "cost_adjustment": "0.0",
                    "gam_deal_type": None,
                    "created_at": "2024-03-22T15:42:56.187Z",
                    "updated_at": "2024-04-01T22:21:34.365Z",
                    "created_by": "Meredith Folsom",
                    "updated_by": "Meredith Folsom",
                    "media_plan_quantity": 1020000000,
                    "media_plan_ecpm": "0.652647058823529411764705882352941176470588235",
                    "quantity_type": "Impressions",
                    "inventory": None,
                    "gross_rate": "0.0",
                    "gross_rate_loc": "0.0",
                    "gross_budget": "0.0",
                    "gross_budget_loc": "5000.0",
                    "discounts": [],
                    "deal_product": None,
                    "package": None,
                    "product": {"id": 212592, "name": "Firefox New Tab US (CPM)"},
                    "rate_card": {"id": 1172, "name": "2024 Rate Card"},
                    "rate_type": {"id": 124, "name": "CPM"},
                    "territory": None,
                    "custom_fields": None,
                    "line_item_monthlies": [
                        {
                            "month": "2024-06",
                            "quantity": "148351648.35",
                            "budget": "137967.032967",
                            "budget_loc": "137967.032967",
                            "est_cost": "0.0",
                            "est_cost_loc": "0.0",
                        },
                        {
                            "month": "2024-05",
                            "quantity": "153296703.3",
                            "budget": "142565.934066",
                            "budget_loc": "142565.934066",
                            "est_cost": "0.0",
                            "est_cost_loc": "0.0",
                        },
                        {
                            "month": "2024-04",
                            "quantity": "148351648.35",
                            "budget": "137967.032967",
                            "budget_loc": "137967.032967",
                            "est_cost": "0.0",
                            "est_cost_loc": "0.0",
                        },
                    ],
                }
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


def mocked_get_product(*args, **kwargs) -> BoostrProduct:
    """Mock out retrieving a product from the DB"""
    return BOOSTR_PRODUCTS[kwargs["boostr_id"]]


BOOSTR_MEDIAPLAN_LINE_ITEMS = {
    1234: BoostrDealMediaPlanLineItem(
        media_plan_line_item_id=10001,
        boostr_deal=28256,
        boostr_product=28256,
        rate_type="CPC",
        rate=Decimal("123456.78"),
        quantity=Decimal("123456.78"),
        budget=Decimal("123456.78"),
        month="09-2024",
    ),
}

BOOSTR_MEDIAPLANS = {
    28256: BoostrMediaPlan(
        media_plan_id=10001,
        name="Test Deal",
        boostr_deal=28256,
        line_items={
            28256: {
                28256: [
                    BoostrDealMediaPlanLineItem(
                        media_plan_line_item_id=265115,
                        boostr_deal=28256,
                        boostr_product=28256,
                        rate_type="CPC",
                        rate=Decimal("123456.78"),
                        quantity=Decimal("123456.78"),
                        budget=Decimal("123456.78"),
                        month="09-2024",
                    )
                ]
            },
        },
    ),
}


def mock_get_media_plans(*args, **kwargs) -> BoostrMediaPlan:
    """Mock out retrieving a media plan from the DB"""
    return BOOSTR_MEDIAPLANS[kwargs["media_plan_id"]]


BOOSTR_DEALS = {
    28256: BoostrDeal(
        boostr_id=28256,
        name="Deal with Customer",
        advertiser="Customer, Inc",
        currency="$",
        amount=5000,
        sales_representatives="asales@mozilla.com",
        start_date="2024-02-01",
        end_date="2024-05-31",
    ),
    1498421: BoostrDeal(
        boostr_id=1498421,
        name="Deal with Customer",
        advertiser="Customer, Inc",
        currency="$",
        amount=5000,
        sales_representatives="asales@mozilla.com",
        start_date="2024-02-01",
        end_date="2024-05-31",
    ),
}


def mocked_get_deal(*args, **kwargs) -> BoostrDeal:
    """Mock out retrieving a product from the DB"""
    return BOOSTR_DEALS[kwargs["boostr_id"]]


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

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch.object(BoostrApi, "authenticate", return_value="im.a.jwt")
    def test_setup_session(self, mock_sleep, mock_authenticate):
        """Test the function that sets up the headers, authenticates with boosrt, and sets up the session"""
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        self.assertEqual(
            boostr.session.headers["Accept"], "application/vnd.boostr.public"
        )
        self.assertEqual(boostr.session.headers["Content-Type"], "application/json")
        self.assertEqual(boostr.session.headers["Authorization"], "Bearer im.a.jwt")

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    def test_authenticate(self, mock_sleep, mock_post):
        """Test authenticate function that calls boostr auth and returns a JWT"""
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        jwt = boostr.authenticate(EMAIL, PASSWORD)
        self.assertEqual(jwt, "i.am.jwt")

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_token_fail)
    def test_authenticate_fail(self, mock_post, mock_sleep):
        """Test sad path for the authenticate function"""
        with self.assertRaises(BoostrApiError):
            BoostrApi("fail/lol", "uhoh@mozilla.com", "uhoh")

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch("consvc_shepherd.models.BoostrProduct.objects.update_or_create")
    def test_upsert_products(
        self, mock_update_or_create, mock_get, mock_post, mock_sleep
    ):
        """Test function that calls boostr API for product data and saves to our DB"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.upsert_products()
        calls = [
            mock.call(
                boostr_id=212592,
                defaults={
                    "full_name": "Firefox 2nd Tile CA (CPM)",
                    "campaign_type": BoostrProduct.CampaignType.CPM,
                },
            ),
            mock.call(
                boostr_id=28256,
                defaults={
                    "full_name": "Firefox New Tab US (CPC)",
                    "campaign_type": BoostrProduct.CampaignType.CPC,
                },
            ),
        ]
        mock_update_or_create.assert_has_calls(calls)

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_fail)
    def test_upsert_products_fail(self, mock_get, mock_post, mock_sleep):
        """Test that upsert_products will raise an API error on non-200 status"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        with self.assertRaises(BoostrApiError):
            loader.upsert_products()

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch(
        "consvc_shepherd.models.BoostrDeal.objects.update_or_create",
        side_effect=mock_update_or_create_deal,
    )
    @mock.patch.object(BoostrLoader, "upsert_deal_products")
    def test_upsert_deals(
        self,
        mock_upsert_deal_products,
        mock_update_or_create,
        mock_get,
        mock_post,
        mock_sleep,
    ):
        """Test function that calls the Boostr API for deal data and saves to our DB"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)

        loader.upsert_deals()
        calls = [
            mock.call(
                boostr_id=1498421,
                name="Neutron: Neutron US, DE, FR",
                advertiser="Neutron",
                currency="$",
                amount=50000,
                sales_representatives="ksales@mozilla.com",
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
        mock_update_or_create.assert_has_calls(calls, any_order=True)

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_fail)
    def test_upsert_deals_fail(self, mock_get, mock_post, mock_sleep):
        """Test that upsert_deals will raise an API error on non-200 status"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        with self.assertRaises(BoostrApiError):
            loader.upsert_deals()

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch(
        "consvc_shepherd.models.BoostrDeal.objects.update_or_create",
        side_effect=mock_update_or_create_deal,
    )
    @mock.patch.object(BoostrLoader, "upsert_deal_products")
    def test_upsert_deals_respects_max_deal_pages_limit(
        self,
        mock_upsert_deal_products,
        mock_update_or_create,
        mock_get,
        mock_post,
        mock_sleep,
    ):
        """Test that upsert_deals respects the given max_deal_pages limit"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD, 3)
        loader.upsert_deals()
        assert 3 == mock_get.call_count

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch(
        "consvc_shepherd.models.BoostrDeal.objects.update_or_create",
        side_effect=mock_update_or_create_deal,
    )
    @mock.patch.object(BoostrLoader, "upsert_deal_products")
    def test_upsert_deals_respects_default_max_deal_pages_limit(
        self,
        mock_upsert_deal_products,
        mock_update_or_create,
        mock_get,
        mock_post,
        mock_sleep,
    ):
        """Test that upsert_deals respects the default max_deal_pages limit"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.upsert_deals()
        assert 50 == mock_get.call_count

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch(
        "consvc_shepherd.models.BoostrProduct.objects.get",
        side_effect=mocked_get_product,
    )
    @mock.patch("consvc_shepherd.models.BoostrDeal.objects.get")
    @mock.patch("consvc_shepherd.models.BoostrDealProduct.objects.update_or_create")
    def test_upsert_deal_products(
        self,
        mock_update_or_create,
        mock_get_deal,
        mock_get_product,
        mock_get,
        mock_post,
        mock_sleep,
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
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD, max_deal_pages=1)
        mock_get_deal.return_value = deal

        loader.upsert_deal_products()

        product = mocked_get_product(boostr_id=28256)

        mock_update_or_create.assert_called_with(
            boostr_deal=deal,
            boostr_product=mocked_get_product(boostr_id=28256),
            month="2024-06",
            budget=10000.0,
        )

        mock_update_or_create.assert_any_call(
            boostr_deal=deal,
            boostr_product=product,
            month="2024-06",
            budget=10000.0,
        )

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_fail)
    def test_upsert_deal_products_fail(self, mock_get, mock_post, mock_sleep):
        """Test that upsert_deal_products will raise an API error on non-200 status"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        with self.assertRaises(BoostrApiError):
            loader.upsert_deal_products()

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

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    def test_boostr_api_post(self, mock_post_success, mock_sleep):
        """Test the BoostrApi POST wrapper"""
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        auth_json = {"auth": {"email": "email@mozilla.com", "password": "test"}}
        post_json = {"info": "for the server"}
        headers = {"X-Boostr-Whatever": "Stuff"}
        response = boostr.post("some-path", json=post_json, headers=headers)
        calls = [
            mock.call(
                f"{BASE_URL}/user_token",
                json=auth_json,
                headers={},
                timeout=15,
            ),
            mock.call(
                f"{BASE_URL}/some-path",
                json=post_json,
                headers=headers,
                timeout=15,
            ),
        ]
        self.assertEqual(response["data"], "wow")
        self.assertEqual(response["count"], 42)
        mock_post_success.assert_has_calls(calls)

    @mock.patch("consvc_shepherd.management.commands.sync_boostr_data")
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    def test_boostr_api_get(self, mock_get_success, mock_post_success, mock_sleep):
        """Test the BoostrApi GET wrapper"""
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        headers = {"X-Boostr-Whatever": "Stuff"}
        products_params = {
            "per": "300",
            "page": "1",
            "filter": "all",
        }
        products = boostr.get("products", headers=headers, params=products_params)
        calls = [
            mock.call(
                f"{BASE_URL}/products",
                params=products_params,
                headers=headers,
                timeout=15,
            ),
        ]

        self.assertEqual(len(products), 2)
        mock_get_success.assert_has_calls(calls)        

    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrLoader.upsert_mediaplan_lineitems"
    )
    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.MediaPlanCollection.add_media_plan"
    )
    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrMediaPlan.add_line_item"
    )
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    def test_upsert_mediaplans(
        self,
        mock_post_success,
        mock_get_success,
        mock_add_line_item,
        mock_add_media_plan,
        mock_upsert_mediaplan_lineitems,
    ):
        # self.new_media_plan = mock.Mock(spec=BoostrMediaPlan)
        # self.upsert_mediaplan_lineitems = mock.Mock()

        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)

        loader.upsert_mediaplan()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>", mock_upsert_mediaplan_lineitems.call_args)
        mock_upsert_mediaplan_lineitems.assert_called_with(
            BoostrMediaPlan(
                media_plan_id=271925,
                name="Fintie: Fintie May - July 2024 Test",
                boostr_deal=1412834,
                line_items={},
            )
        )
        mock_add_media_plan.assert_called_with(
            1412834,
            BoostrMediaPlan(
                media_plan_id=271925,
                name="Fintie: Fintie May - July 2024 Test",
                boostr_deal=1412834,
                line_items={},
            ),
        )

    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrMediaPlan.add_line_item"
    )
    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrProduct.objects.get",
        side_effect=mocked_get_product,
    )
    @mock.patch(
        "consvc_shepherd.models.BoostrDeal.objects.get", side_effect=mocked_get_deal
    )
    # @mock.patch("consvc_shepherd.models.BoostrProduct")
    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrDealProduct.objects.filter"
    )
    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrDealProduct.objects.update"
    )
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    def test_upsert_mediaplan_lineitems(
        self,
        mock_post_success,
        mock_get_success,
        mock_update,
        mock_filter,
        mock_get_deal,
        mock_get_product,
        mock_add_line_item,
    ):
        self.media_plan = mock.Mock(spec=BoostrMediaPlan)
        mock_qs = mock.Mock()
        mock_filter.return_value = mock_qs
        mock_update.return_value = mock.Mock()
        media_plan = BOOSTR_MEDIAPLANS[28256]
        self.media_plan.media_plan_id = media_plan.media_plan_id
        self.media_plan.name = media_plan.name
        self.media_plan.boostr_deal = media_plan.boostr_deal

        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)

        loader.upsert_mediaplan_lineitems(media_plan=self.media_plan)

        self.media_plan.add_line_item.assert_called_with(
            BoostrDealMediaPlanLineItem(
                media_plan_line_item_id=28254111111,
                boostr_deal=28256,
                boostr_product=212592,
                rate_type="CPM",
                rate="0.93",
                quantity="148351648.35",
                budget="137967.032967",
                month="2024-04",
            )
        )

        mock_filter.assert_called_with(
            month="2024-04", boostr_deal_id=28256, boostr_product_id=212592
        )

        mock_filter.return_value.update.assert_called_with(
            quantity="148351648.35", rate="0.93", rate_type="CPM"
        )

        loader.li_mp_data = None
        loader.upsert_mediaplan_lineitems(media_plan=self.media_plan)
        mock_get_product.assert_called()

    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrLoader.upsert_products"
    )
    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrLoader.upsert_deals"
    )
    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrLoader.upsert_deal_products"
    )
    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.logging.getLogger"
    )
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    def test_load_called_without_exceptions(
        self,
        mock_get_success,
        mock_post_success,
        mock_get_logger,
        mock_upsert_deal_products,
        mock_upsert_deals,
        mock_upsert_products,
    ):
        mock_logger = mock.Mock()
        mock_get_logger.return_value = mock_logger

        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.load()
        mock_upsert_products.assert_called_once()
        mock_upsert_deals.assert_called_once()
        mock_upsert_deal_products.assert_called_once()
