# Generated by Django 4.2.15 on 2024-09-13 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consvc_shepherd", "0012_remove_boostrsyncstatus_created_on"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveredCampaign",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("submission_date", models.DateTimeField()),
                ("flight_id", models.BigIntegerField(unique=True)),
                ("campaign_id", models.BigIntegerField()),
                ("surface", models.CharField()),
                ("country", models.CharField()),
                ("product", models.CharField()),
                ("provider", models.CharField()),
                ("clicks", models.IntegerField()),
                ("impressions", models.IntegerField()),
            ],
        ),
    ]