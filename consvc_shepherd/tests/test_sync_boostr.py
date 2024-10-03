"""Unit tests for the sync_boostr_data command"""

from unittest import mock

from django.test import TestCase, override_settings

from consvc_shepherd.management.commands.sync_boostr_data import (
    BoostrApi,
    BoostrApiError,
    BoostrApiMaxRetriesError,
    BoostrDeal,
    BoostrLoader,
    BoostrProduct,
    get_campaign_type,
)
from consvc_shepherd.tests.test_sync_boostr_mocks import (
    mock_get_fail,
    mock_get_fail_500,
    mock_get_latest_boostr_sync_status,
    mock_get_product,
    mock_get_success,
    mock_get_success_response,
    mock_post_success,
    mock_post_token_fail,
    mock_request_exception,
    mock_too_many_requests_response,
    mock_update_or_create_deal,
    mock_upsert_deals_exception,
)

BASE_URL = "https://example.com"
EMAIL = "email@mozilla.com"
PASSWORD = "test"  # nosec
DEFAULT_RETRY_INTERVAL = 60
MOCK_RETRY_AFTER_SECONDS = 60
MAX_RETRY = 5


@override_settings(DEBUG=True)
class TestSyncBoostrData(TestCase):
    """Unit tests for functions that fetch from boostr API and store in our DB"""

    @mock.patch.object(BoostrApi, "authenticate", return_value="im.a.jwt")
    def test_setup_session(self, mock_authenticate):
        """Test the function that sets up the headers, authenticates with boosrt, and sets up the session"""
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        self.assertEqual(
            boostr.session.headers["Accept"], "application/vnd.boostr.public"
        )
        self.assertEqual(boostr.session.headers["Content-Type"], "application/json")
        self.assertEqual(boostr.session.headers["Authorization"], "Bearer im.a.jwt")

    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    def test_authenticate(self, mock_post):
        """Test authenticate function that calls boostr auth and returns a JWT"""
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        jwt = boostr.authenticate(EMAIL, PASSWORD)
        self.assertEqual(jwt, "i.am.jwt")

    @mock.patch("time.sleep", return_value=None)
    @mock.patch("requests.Session.get")
    @mock.patch("requests.Session.post")
    def test_429_error(self, mock_post, mock_get, mock_sleep):
        """Test get function for 429 error handling"""
        mock_429_response = mock_too_many_requests_response()
        mock_response = mock_get_success_response()
        mock_get.side_effect = [mock_429_response, mock_response]
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        with self.assertLogs("sync_boostr_data", level="INFO") as captured_logs:
            response = boostr.get("deals")
        mock_sleep.assert_called_once_with(MOCK_RETRY_AFTER_SECONDS + 1)
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(response, {"data": "success"})
        self.assertIn(
            f"INFO:sync_boostr_data:429: Rate limited - Waiting {MOCK_RETRY_AFTER_SECONDS+1} seconds. Current retry: 0",
            captured_logs.output,
        )

    @mock.patch("time.sleep", return_value=None)
    @mock.patch("requests.Session.get", side_effect=mock_get_fail_500)
    @mock.patch("requests.Session.post")
    def test_500_error(self, mock_post, mock_get, mock_sleep):
        """Test sad path for the authenticate function"""
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        with self.assertRaises(BoostrApiError) as context:
            boostr.get("deals")
        self.assertEqual(str(context.exception), "Bad response status 500 from /deals")

    @mock.patch("time.sleep", return_value=None)
    @mock.patch("requests.Session.get")
    @mock.patch("requests.Session.post")
    def test_max_retries(self, mock_post, mock_get, mock_sleep):
        """Test get function for 429 error handling"""
        mock_429_response = mock_too_many_requests_response()
        mock_get.side_effect = [mock_429_response for _ in range(MAX_RETRY)]
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        with self.assertLogs("sync_boostr_data", level="INFO") as captured_logs:
            with self.assertRaises(BoostrApiMaxRetriesError) as context:
                boostr.get("deals")
        self.assertEqual(mock_sleep.call_count, MAX_RETRY)
        self.assertEqual(mock_get.call_count, MAX_RETRY)
        self.assertEqual(str(context.exception), "Maximum retries reached")

        for i in range(MAX_RETRY):
            expected_log = (
                f"INFO:sync_boostr_data:429: Rate limited - "
                f"Waiting {MOCK_RETRY_AFTER_SECONDS+1} seconds. Current retry: {i}"
            )
            self.assertIn(
                expected_log,
                captured_logs.output[i],
            )

    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrApi._sleep",
        return_value=None,
    )
    @mock.patch("requests.Session.get")
    @mock.patch("requests.Session.post")
    def test_api_request_with_request_exception(self, mock_post, mock_get, mock_sleep):
        """Testing GET request with RequestException and a retry"""
        mock_exception = mock_request_exception()
        mock_response = mock_get_success_response()
        mock_get.side_effect = [mock_exception, mock_response]
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        response = boostr.get("deals")
        mock_sleep.assert_called_once_with(DEFAULT_RETRY_INTERVAL)
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(response, {"data": "success"})

    @mock.patch("time.sleep", return_value=None)
    @mock.patch("requests.Session.post", side_effect=mock_post_token_fail)
    def test_authenticate_fail(self, mock_post, mock_sleep):
        """Test sad path for the authenticate function"""
        with self.assertRaises(BoostrApiError):
            BoostrApi("fail/lol", "uhoh@mozilla.com", "uhoh")

    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch("consvc_shepherd.models.BoostrProduct.objects.update_or_create")
    def test_upsert_products(self, mock_update_or_create, mock_get, mock_post):
        """Test function that calls boostr API for product data and saves to our DB"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.upsert_products()
        calls = [
            mock.call(
                boostr_id=212592,
                defaults={
                    "full_name": "Firefox 2nd Tile CA (CPM)",
                    "country": "CA",
                    "campaign_type": BoostrProduct.CampaignType.CPM,
                },
            ),
            mock.call(
                boostr_id=28256,
                defaults={
                    "full_name": "Firefox New Tab US (CPC)",
                    "country": "US",
                    "campaign_type": BoostrProduct.CampaignType.CPC,
                },
            ),
        ]
        mock_update_or_create.assert_has_calls(calls)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_fail)
    def test_upsert_products_fail(self, mock_get, mock_post, mock_sleep):
        """Test that upsert_products will raise an API error on non-200 status"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        with self.assertRaises(BoostrApiError):
            loader.upsert_products()

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
    ):
        """Test function that calls the Boostr API for deal data and saves to our DB"""
        self.skipTest(
            "Currently hangs with the addition of the last upsert_deal_products mock"
        )
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.upsert_deals()
        calls = [
            mock.call(
                boostr_id=1498421,
                defaults={
                    "name": "Neutron: Neutron US, DE, FR",
                    "advertiser": "Neutron",
                    "currency": "$",
                    "amount": 50000,
                    "sales_representatives": "ksales@mozilla.com,lsales@mozilla.com",
                    "start_date": "2024-04-01",
                    "end_date": "2024-06-30",
                },
            ),
            mock.call(
                boostr_id=1482241,
                defaults={
                    "name": "HiProduce: CA Tiles May 2024",
                    "advertiser": "HiProduce",
                    "currency": "$",
                    "amount": 10000,
                    "sales_representatives": "jsales@mozilla.com",
                    "start_date": "2024-05-01",
                    "end_date": "2024-05-31",
                },
            ),
        ]
        mock_update_or_create.assert_has_calls(calls)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_fail)
    def test_upsert_deals_fail(self, mock_get, mock_post, mock_sleep):
        """Test that upsert_deals will raise an API error on non-200 status"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        with self.assertRaises(BoostrApiError):
            loader.upsert_deals()

    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch(
        "consvc_shepherd.models.BoostrDeal.objects.update_or_create",
        side_effect=mock_update_or_create_deal,
    )
    @mock.patch.object(BoostrLoader, "upsert_deal_products")
    @mock.patch.object(BoostrLoader, "create_campaign")
    def test_upsert_deals_respects_max_deal_pages_limit(
        self,
        mock_upsert_deal_products,
        mock_create_campaign,
        mock_update_or_create,
        mock_get,
        mock_post,
    ):
        """Test that upsert_deals respects the given max_deal_pages limit"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD, {"max_deal_pages": 3})
        loader.upsert_deals()
        assert 3 == mock_get.call_count
        mock_create_campaign.assert_called()

    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch(
        "consvc_shepherd.models.BoostrDeal.objects.update_or_create",
        side_effect=mock_update_or_create_deal,
    )
    @mock.patch.object(BoostrLoader, "upsert_deal_products")
    @mock.patch.object(BoostrLoader, "create_campaign")
    def test_upsert_deals_respects_default_max_deal_pages_limit(
        self,
        mock_upsert_deal_products,
        mock_create_campaign,
        mock_update_or_create,
        mock_get,
        mock_post,
    ):
        """Test that upsert_deals respects the default max_deal_pages limit"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.upsert_deals()
        assert 50 == mock_get.call_count
        mock_create_campaign.assert_called()

    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
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

    @mock.patch("time.sleep", return_value=None)
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_fail)
    def test_upsert_deal_products_fail(self, mock_get, mock_post, mock_sleep):
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

    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch(
        "consvc_shepherd.models.BoostrProduct.objects.get", side_effect=mock_get_product
    )
    @mock.patch("consvc_shepherd.models.BoostrDealProduct.objects.update_or_create")
    def test_upsert_media_plans(
        self, mock_update_or_create, mock_get_product, mock_get, mock_post
    ):
        """Test function that tests updating deal products with media plan data"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.upsert_mediaplan()

        media_plans_calls = [
            mock.call(
                f"{BASE_URL}/media_plans",
                params={"per": "300", "page": "0", "filter": "all"},
                headers={},
                timeout=15,
            ),
            mock.call(
                f"{BASE_URL}/media_plans/265115/line_items",
                params={"per": "300", "page": "1", "filter": "all"},
                headers={},
                timeout=15,
            ),
            mock.call(
                f"{BASE_URL}/media_plans/271925/line_items",
                params={"per": "300", "page": "1", "filter": "all"},
                headers={},
                timeout=15,
            ),
            mock.call(
                f"{BASE_URL}/media_plans/269031/line_items",
                params={"per": "300", "page": "1", "filter": "all"},
                headers={},
                timeout=15,
            ),
        ]
        mock_get.assert_has_calls(media_plans_calls)

    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_fail)
    @mock.patch(
        "consvc_shepherd.models.BoostrProduct.objects.get", side_effect=mock_get_product
    )
    @mock.patch("consvc_shepherd.models.BoostrDealProduct.objects.update_or_create")
    def test_upsert_media_plans_fail(
        self, mock_update_or_create, mock_get_product, mock_get, mock_post
    ):
        """Test function that tests updating deal products with media plan data"""

        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        with self.assertRaises(BoostrApiError) as context:
            loader.upsert_mediaplan()

        self.assertEqual(
            str(context.exception), "Bad response status 400 from /media_plans"
        )

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

    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    def test_boostr_api_post(self, mock_post_success):
        """Test the BoostrApi POST wrapper"""
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        auth_json = {"auth": {"email": "email@mozilla.com", "password": "test"}}
        post_json = {"info": "for the server"}
        headers = {"X-Boostr-Whatever": "Stuff"}
        response = boostr.post("some-path", json=post_json, headers=headers)
        post_calls = [
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
        mock_post_success.assert_has_calls(post_calls)

    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    def test_boostr_api_get(self, mock_get_success, mock_post_success):
        """Test the BoostrApi GET wrapper"""
        boostr = BoostrApi(BASE_URL, EMAIL, PASSWORD)
        headers = {"X-Boostr-Whatever": "Stuff"}
        products_params = {
            "per": "300",
            "page": "1",
            "filter": "all",
        }
        products = boostr.get("products", headers=headers, params=products_params)
        get_calls = [
            mock.call(
                f"{BASE_URL}/products",
                params=products_params,
                headers=headers,
                timeout=15,
            ),
        ]
        self.assertEqual(len(products), 2)
        mock_get_success.assert_has_calls(get_calls)

    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch("consvc_shepherd.models.BoostrSyncStatus.objects.create")
    def test_update_sync_status(
        self,
        mock_create,
        mock_get,
        mock_post,
    ):
        """Test the update_sync_status function"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.update_sync_status(
            "success", "2024-05-22 16:52:34.369769+00:00", "Boostr sync success"
        )
        calls = [
            mock.call(
                status="success",
                synced_on="2024-05-22 16:52:34.369769+00:00",
                message="Boostr sync success",
            ),
        ]
        mock_create.assert_has_calls(calls)

    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrLoader.upsert_products"
    )
    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrLoader.upsert_deals"
    )
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch("consvc_shepherd.models.BoostrSyncStatus.objects.create")
    def test_load_success(
        self,
        mock_create,
        mock_get,
        mock_post,
        mock_upsert_deals,
        mock_upsert_products,
    ):
        """Test the load function success scenario"""
        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        loader.load()
        calls = [
            mock.call(
                status="success",
                synced_on=mock.ANY,
                message="Boostr sync success",
            ),
        ]
        mock_create.assert_has_calls(calls)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "consvc_shepherd.management.commands.sync_boostr_data.BoostrLoader.upsert_deals",
        side_effect=mock_upsert_deals_exception,
    )
    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch("consvc_shepherd.models.BoostrSyncStatus.objects.create")
    def test_load_failure(
        self, mock_create, mock_get, mock_post, mock_upsert_products, mock_sleep
    ):
        """Test the load function failure scenario"""
        with self.assertRaises(Exception):
            loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
            loader.load()
            calls = [
                mock.call(
                    status="failure",
                    synced_on=mock.ANY,
                    message=mock.ANY,
                ),
            ]
            mock_create.assert_has_calls(calls)

    @mock.patch("requests.Session.post", side_effect=mock_post_success)
    @mock.patch("requests.Session.get", side_effect=mock_get_success)
    @mock.patch("consvc_shepherd.models.BoostrSyncStatus.objects.filter")
    def test_get_latest_sync_status(self, mock_filter, mock_get, mock_post):
        """Test the get_latest_sync_status function"""
        filter_return_value_mock = mock.MagicMock()

        mock_filter.return_value = filter_return_value_mock
        filter_return_value_mock.__len__.return_value = 3
        filter_return_value_mock.latest.return_value = (
            mock_get_latest_boostr_sync_status()
        )

        loader = BoostrLoader(BASE_URL, EMAIL, PASSWORD)
        synced_on = loader.get_latest_sync_status()
        self.assertEqual(synced_on, "2024-09-22 16:52:34.369769+00:00")
