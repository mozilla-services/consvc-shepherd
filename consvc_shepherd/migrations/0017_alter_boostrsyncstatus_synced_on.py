# Generated by Django 4.2.16 on 2024-09-27 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consvc_shepherd", "0016_alter_campaign_net_spend"),
    ]

    operations = [
        migrations.AlterField(
            model_name="boostrsyncstatus",
            name="synced_on",
            field=models.DateTimeField(),
        ),
    ]