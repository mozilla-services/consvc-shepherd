"""This script generates mock data to test our models which get displayed in the Admin page"""

import random
import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from consvc_shepherd.models import (
    AllocationSetting,
    BoostrDeal,
    BoostrDealProduct,
    BoostrProduct,
    BoostrSyncStatus,
    Campaign,
    DeliveredFlight,
    PartnerAllocation,
)
from contile.models import Partner

fake = Faker()


class Command(BaseCommand):
    """Django admin custom command for populating the dev DB with some mock data"""

    help = "Seed the database with initial data for consvc_shepherd"

    def handle(self, *args, **kwargs):
        """Handle running the command"""
        # Get or create user
        User = get_user_model()
        user, _ = User.objects.get_or_create(username="admin", defaults={"password": "adminpass"})

        # Create multiple partners
        for _ in range(5):
            Partner.objects.get_or_create(name=secrets.choice(["Kevel", "ADM"]))

        partners = list(Partner.objects.all())

        # Create multiple Boostr Products
        for i in range(10):
            BoostrProduct.objects.get_or_create(
                boostr_id=i + 1,
                defaults={
                    "full_name": fake.catch_phrase(),
                    "country": fake.country_code(),
                    "campaign_type": secrets.choice(["CPC", "CPM"]),
                },
            )

        products = list(BoostrProduct.objects.all())

        # Create multiple Boostr Deals
        for i in range(10):
            BoostrDeal.objects.get_or_create(
                boostr_id=i + 1,
                defaults={
                    "name": f"Deal {i + 1} - {fake.company()}",
                    "advertiser": fake.company(),
                    "currency": secrets.choice(["$", "€", "£"]),
                    "amount": secrets.randbelow(150001) + 50000,
                    "sales_representatives": fake.name(),
                    "start_date": fake.date_this_year(before_today=True, after_today=False),
                    "end_date": fake.date_this_year(before_today=False, after_today=True),
                },
            )

        deals = list(BoostrDeal.objects.all())

        # Create Boostr Deal Products
        for _ in range(10):
            BoostrDealProduct.objects.get_or_create(
                boostr_deal=secrets.choice(deals),
                boostr_product=secrets.choice(products),
                defaults={
                    "budget": secrets.randbelow(90001) + 10000,
                    "month": fake.date_between(start_date="-12m", end_date="now").strftime("%Y-%m"),
                },
            )

        # Create Allocation Settings and Partner Allocations
        for i in range(3):
            allocation_setting, _ = AllocationSetting.objects.get_or_create(position=i + 1)
            for partner in partners[:2]:  # Randomly allocate 2 partners
                PartnerAllocation.objects.get_or_create(
                    allocation_position=allocation_setting,
                    partner=partner,
                    defaults={"percentage": (secrets.randbelow(81) + 10)},
                )

        # Create multiple campaigns
        for i in range(10):
            Campaign.objects.get_or_create(
                kevel_flight_id=i + 1,
                defaults={
                    "ad_ops_person": fake.name(),
                    "notes": fake.sentence(),
                    "net_spend": random.uniform(50000.00, 200000.00),  # nosec  # noqa: S311
                    "impressions_sold": secrets.randbelow(4900001) + 100000,
                    "seller": fake.company(),
                    "deal": secrets.choice(deals),
                    "start_date": fake.date_this_year(before_today=True, after_today=False),
                    "end_date": fake.date_this_year(before_today=False, after_today=True),
                },
            )

        # Create multiple delivered flights
        for _ in range(10):
            DeliveredFlight.objects.get_or_create(
                submission_date=fake.date_between(start_date="-6m", end_date="now"),
                campaign_id=secrets.randbelow(10) + 1,
                campaign_name=fake.text(max_nb_chars=10),
                flight_id=secrets.randbelow(10) + 1,
                flight_name=fake.color_name(),
                defaults={
                    "country": fake.country_code(),
                    "provider": secrets.choice(["Kevel", "ADM"]),
                    "clicks_delivered": secrets.randbelow(100) + 1,
                    "impressions_delivered": secrets.randbelow(900) + 100,
                },
            )

        # Create multiple BoostrSyncStatus
        for _ in range(10):
            BoostrSyncStatus.objects.get_or_create(
                synced_on=timezone.make_aware(fake.date_time_between(start_date="-6m", end_date="now")),
                defaults={
                    "status": secrets.choice(["success", "failure"]),
                    "message": fake.sentence(),
                },
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database with random data"))
