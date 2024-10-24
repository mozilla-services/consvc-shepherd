# Generated by Django 4.2.16 on 2024-10-13 19:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consvc_shepherd", "0022_alter_boostrsyncstatus_options_and_more_updated"),
    ]

    operations = [
        migrations.CreateModel(
            name="Advertiser",
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
                ("name", models.CharField(unique=True)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name="boostrdeal",
            name="advertiser_id",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="consvc_shepherd.advertiser",
            ),
        ),
    ]
