# Generated by Django 4.2.16 on 2024-09-20 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consvc_shepherd", "0013_campaignsummary_campaign"),
    ]

    operations = [
        migrations.AlterField(
            model_name="campaign",
            name="ad_ops_person",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="campaign",
            name="kevel_flight_id",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="campaign",
            name="notes",
            field=models.CharField(blank=True, null=True),
        ),
    ]