"""Django admin custom command for populating the dev DB with some mock data"""

from django.core.management.base import BaseCommand
from consvc_shepherd.models import (
    AllocationSetting, PartnerAllocation, BoostrProduct, BoostrDeal,
    BoostrDealProduct, BoostrSyncStatus, Campaign, DeliveredCampaign
)
from django.utils import timezone
from contile.models import Partner
from django.contrib.auth import get_user_model
from faker import Faker
import random

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with initial data for consvc_shepherd"

    def handle(self, *args, **kwargs):
        # Get or create user
        User = get_user_model()
        user, _ = User.objects.get_or_create(username="admin", defaults={"password": "adminpass"})

        # Create multiple partners
        for _ in range(5):
            Partner.objects.get_or_create(
                name=random.choice(["kevel", "adm"])
            )

        partners = list(Partner.objects.all())

        # Create multiple Boostr Products
        for i in range(10):
            BoostrProduct.objects.get_or_create(
                boostr_id=i + 1,
                defaults={
                    "full_name": fake.catch_phrase(),
                    "country": fake.country_code(),
                    "campaign_type": random.choice(["CPC", "CPM"])
                }
            )

        products = list(BoostrProduct.objects.all())

        # Create multiple Boostr Deals
        for i in range(10):
            BoostrDeal.objects.get_or_create(
                boostr_id=i + 1,
                defaults={
                    "name": f"Deal {i + 1} - {fake.company()}",
                    "advertiser": fake.company(),
                    "currency": random.choice(["$", "€", "£"]),
                    "amount": random.randint(50000, 200000),
                    "sales_representatives": fake.name(),
                    "start_date": fake.date_this_year(before_today=True, after_today=False),
                    "end_date": fake.date_this_year(before_today=False, after_today=True),
                }
            )

        deals = list(BoostrDeal.objects.all())

        # Create Boostr Deal Products
        for _ in range(10):
            BoostrDealProduct.objects.get_or_create(
                boostr_deal=random.choice(deals),
                boostr_product=random.choice(products),
                defaults={
                    "budget": random.randint(10000, 100000),
                    "month": fake.date_between(start_date="-12m", end_date="now").strftime('%Y-%m')
                }
            )

        # Create Allocation Settings and Partner Allocations
        for i in range(3):
            allocation_setting, _ = AllocationSetting.objects.get_or_create(position=i + 1)
            for partner in partners[:2]:  # Randomly allocate 2 partners
                PartnerAllocation.objects.get_or_create(
                    allocation_position=allocation_setting,
                    partner=partner,
                    defaults={"percentage": random.randint(10, 90)}
                )

        # Create multiple campaigns
        for i in range(10):
            Campaign.objects.get_or_create(
                kevel_flight_id=i + 1,
                defaults={
                    "ad_ops_person": fake.name(),
                    "notes": fake.sentence(),
                    "net_spend": random.uniform(50000.00, 200000.00),
                    "impressions_sold": random.randint(100000, 5000000),
                    "seller": fake.company(),
                    "deal": random.choice(deals),
                    "start_date": fake.date_this_year(before_today=True, after_today=False),
                    "end_date": fake.date_this_year(before_today=False, after_today=True),
                }
            )

        campaigns = list(Campaign.objects.all())

        # Create multiple delivered campaigns
        for _ in range(10):
            DeliveredCampaign.objects.get_or_create(
                submission_date=fake.date_between(start_date="-6m", end_date="now"),
                campaign_id=random.randint(1, 20),
                flight=random.choice(campaigns),
                defaults={
                    "country": fake.country_code(),
                    "provider": random.choice(["Kevel", "Contile"]),
                    "clicks_delivered": random.randint(1, 100),
                    "impressions_delivered": random.randint(100, 1000)
                }
            )

        # Create multiple BoostrSyncStatus
        for _ in range(10):
            BoostrSyncStatus.objects.get_or_create(
                synced_on = timezone.make_aware(fake.date_time_between(start_date="-6m", end_date="now")),
                defaults={"status": random.choice(["success", "failure"]), "message": fake.sentence()}
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database with random data"))
