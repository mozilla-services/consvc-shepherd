# Generated by Django 4.2.14 on 2024-08-16 16:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consvc_shepherd", "0009_alter_boostrproduct_campaign_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="BoostrDealMediaPlan",
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
                ("media_plan_id", models.IntegerField()),
                ("name", models.CharField(null=True)),
                (
                    "boostr_deal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="consvc_shepherd.boostrdeal",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BoostrDealMediaPlanLineItem",
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
                ("media_plan_line_item_id", models.IntegerField(null=True)),
                (
                    "rate_type",
                    models.CharField(
                        choices=[("CPM", "CPM"), ("CPC", "CPC"), ("FF", "Flat Fee")],
                        default="CPM",
                    ),
                ),
                (
                    "rate",
                    models.DecimalField(decimal_places=2, max_digits=13, null=True),
                ),
                ("quantity", models.PositiveIntegerField(null=True)),
                (
                    "budget",
                    models.DecimalField(decimal_places=2, max_digits=13, null=True),
                ),
                (
                    "media_plan_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="consvc_shepherd.boostrdealmediaplan",
                    ),
                ),
            ],
        ),
    ]