"""Unit tests for the Campaign, Product, and Deal view sets in the consvc_shepherd API."""

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from consvc_shepherd.api.serializers import (
    BoostrDealSerializer,
    BoostrProductSerializer,
    CampaignSerializer,
)
from consvc_shepherd.models import BoostrDeal, BoostrProduct, Campaign, Flight


@override_settings(DEBUG=True)
class ProductViewSetTests(APITestCase):
    """Unit tests for ProductViewSet."""

    def setUp(self):
        """Set up test data."""
        self.product1 = BoostrProduct.objects.create(
            boostr_id=1, full_name="Product1", campaign_type="CPC"
        )
        self.product2 = BoostrProduct.objects.create(
            boostr_id=2, full_name="Product2", campaign_type="CPC"
        )

    def test_get_all_products(self):
        """Test fetching all products via GET request."""
        response = self.client.get(reverse("products-list"))
        products = BoostrProduct.objects.all()
        serializer = BoostrProductSerializer(products, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


@override_settings(DEBUG=True)
class BoostrDealViewSetTests(APITestCase):
    """Unit tests for BoostrDealViewSet."""

    def setUp(self):
        """Set up test data."""
        self.deal1 = BoostrDeal.objects.create(
            boostr_id=1,
            name="Test Deal1",
            advertiser="Test Advertiser1",
            currency="$",
            amount=10000,
            sales_representatives="Rep1, Rep2",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        self.deal2 = BoostrDeal.objects.create(
            boostr_id=2,
            name="Test Deal2",
            advertiser="Test Advertiser2",
            currency="$",
            amount=10000,
            sales_representatives="Rep1, Rep2",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
        self.url = reverse("deals-list")

    def test_get_all_deals(self):
        """Test fetching all deals via GET request."""
        response = self.client.get(self.url)
        deals = BoostrDeal.objects.all()
        serializer = BoostrDealSerializer(deals, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


@override_settings(DEBUG=True)
class CampaignViewSetTests(APITestCase):
    """Unit tests for CampaignViewSet."""

    def setUp(self):
        """Set up test data."""
        self.deal1 = BoostrDeal.objects.create(
            boostr_id=1,
            name="Test Deal1",
            advertiser="Test Advertiser1",
            currency="$",
            amount=10000,
            sales_representatives="Rep1, Rep2",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
        self.deal2 = BoostrDeal.objects.create(
            boostr_id=2,
            name="Test Deal2",
            advertiser="Test Advertiser2",
            currency="$",
            amount=5000,
            sales_representatives="Rep1, Rep2",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        self.campaign1 = Campaign.objects.create(
            notes="Initial campaign",
            ad_ops_person="Leanne",
            impressions_sold=4,
            net_spend=10000,
            deal=self.deal1,
            start_date="2023-01-01",
            end_date="2023-01-03",
            seller="Meredith",
        )

        self.campaign2 = Campaign.objects.create(
            notes="Second campaign",
            ad_ops_person="John",
            impressions_sold=2,
            net_spend=5000,
            deal=self.deal2,
            start_date="2023-02-01",
            end_date="2023-02-03",
            seller="Sarah",
        )

        Flight.objects.create(
            campaign=self.campaign1,
            flight_id=123,
        )

        Flight.objects.create(
            campaign=self.campaign2,
            flight_id=456,
        )

        self.url = reverse("campaigns-list")

    def test_get_all_campaigns(self):
        """Test fetching all campaigns via GET request."""
        response = self.client.get(self.url)
        campaigns = Campaign.objects.all()
        serializer = CampaignSerializer(campaigns, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_validate_campaign_success(self):
        """Test successful creation of a campaign when net_spend matches the deal's amount."""
        data = {
            "notes": "New campaign",
            "ad_ops_person": "Alice",
            "kevel_flight_id": 789,
            "impressions_sold": 1,
            "net_spend": 10000,
            "deal": self.deal1.id,
            "start_date": "2023-03-01",
            "end_date": "2023-03-03",
            "seller": "Tom",
            "campaign_fields": [],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Campaign.objects.count(), 3)

    def test_create_validate_campaign_failure(self):
        """Test failure to create a campaign when net_spend does not match the deal's amount."""
        data = {
            "notes": "New campaign",
            "ad_ops_person": "Alice",
            "kevel_flight_id": 789,
            "impressions_sold": 1,
            "net_spend": 4865,
            "deal": self.deal1.id,
            "start_date": "2023-03-01",
            "end_date": "2023-03-03",
            "seller": "Tom",
            "campaign_fields": [],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_campaign(self):
        """Test updating an existing campaign via PUT request."""
        data = {
            "notes": "New campaign updated",
            "ad_ops_person": "Alice",
            "kevel_flight_id": 789,
            "impressions_sold": 1,
            "net_spend": 10000,
            "deal": self.deal1.id,
            "start_date": "2023-03-01",
            "end_date": "2023-03-03",
            "seller": "Tom",
            "campaign_fields": [],
        }
        campaign_url = reverse("campaigns-detail", args=[self.campaign1.id])
        response = self.client.put(campaign_url, data, format="json")
        self.campaign1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.campaign1.notes, "New campaign updated")

    def test_delete_campaign(self):
        """Test deleting an existing campaign via DELETE request."""
        product_url = reverse("campaigns-detail", args=[self.campaign1.id])
        response = self.client.delete(product_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Campaign.objects.count(), 1)

    def test_split_create_update_campaigns(self):
        """Test creating and updating campaigns in split."""
        data = [
            {
                "id": self.campaign1.id,
                "notes": "Updated campaign",
                "ad_ops_person": "Alice",
                "kevel_flight_id": 123,
                "impressions_sold": 2,
                "net_spend": 5000,
                "deal": self.deal1.id,
                "start_date": "2023-03-01",
                "end_date": "2023-03-03",
                "seller": "Tom",
            },
            {
                "notes": "New campaign",
                "ad_ops_person": "Bob",
                "kevel_flight_id": 789,
                "impressions_sold": 2,
                "net_spend": 5000,
                "deal": self.deal1.id,
                "start_date": "2023-03-01",
                "end_date": "2023-03-03",
                "seller": "Alice",
            },
        ]
        campaigns_data = {"campaigns": data, "deal": self.deal1.id}
        campaign_split_url = reverse("campaigns-split-campaigns")

        response = self.client.post(campaign_split_url, campaigns_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Campaign.objects.count(), 3)

        self.campaign1.refresh_from_db()
        self.assertEqual(self.campaign1.notes, "Updated campaign")
