# Generated by Django 4.0.2 on 2022-03-23 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consvc_shepherd", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="advertiserurl",
            name="domain",
            field=models.CharField(max_length=255),
        ),
    ]
