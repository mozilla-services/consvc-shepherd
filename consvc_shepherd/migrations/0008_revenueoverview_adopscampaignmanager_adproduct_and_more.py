# Generated by Django 4.2.14 on 2024-08-28 22:21

import consvc_shepherd.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contile', '0005_remove_partner_click_hosts_and_more'),
        ('consvc_shepherd', '0007_alter_partnerallocation_partner_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RevenueOverview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placement', models.CharField()),
                ('revenue', models.IntegerField()),
                ('budget', models.IntegerField()),
                ('revenue_delta', models.IntegerField()),
                ('month', models.DateField()),
            ],
            options={
                'db_table': 'revenue_overview',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AdOpsCampaignManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AdProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField()),
            ],
        ),
        migrations.CreateModel(
            name='BoostrDeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boostr_id', models.IntegerField(unique=True)),
                ('name', models.CharField()),
                ('advertiser', models.CharField()),
                ('currency', models.CharField()),
                ('amount', models.IntegerField()),
                ('sales_representatives', models.CharField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('campaign_manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='consvc_shepherd.adopscampaignmanager')),
            ],
        ),
        migrations.CreateModel(
            name='BoostrProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boostr_id', models.IntegerField(unique=True)),
                ('full_name', models.CharField()),
                ('campaign_type', models.CharField(choices=[('CPC', 'Cpc'), ('CPM', 'Cpm'), ('Flat Fee', 'Flat Fee'), ('None', 'None')])),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=2, unique=True)),
                ('name', models.CharField(default='US', max_length=100)),
            ],
            options={
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='KevelFlight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_id', models.PositiveIntegerField(null=True)),
                ('name', models.CharField(default='Flight', max_length=100)),
                ('start_date', models.DateField(auto_now=True)),
                ('end_date', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='KevelAdvertiser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('contile.advertiser',),
        ),
        migrations.CreateModel(
            name='KevelCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_id', models.PositiveIntegerField()),
                ('advertiser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consvc_shepherd.keveladvertiser')),
                ('flight_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consvc_shepherd.kevelflight')),
            ],
        ),
        migrations.CreateModel(
            name='BoostrDealProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('budget', models.IntegerField()),
                ('month', models.CharField()),
                ('boostr_deal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consvc_shepherd.boostrdeal')),
                ('boostr_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consvc_shepherd.boostrproduct')),
            ],
        ),
        migrations.AddField(
            model_name='boostrdeal',
            name='products',
            field=models.ManyToManyField(related_name='products', through='consvc_shepherd.BoostrDealProduct', to='consvc_shepherd.boostrproduct'),
        ),
        migrations.CreateModel(
            name='AdsInventoryForecast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField(default=datetime.date.today, verbose_name='Month & Year')),
                ('forecast', models.IntegerField(default=10)),
                ('country', models.ForeignKey(default=consvc_shepherd.models.Country.get_default_country, on_delete=django.db.models.deletion.CASCADE, to='consvc_shepherd.country')),
            ],
            options={
                'ordering': ['month', 'country__code'],
            },
        ),
        migrations.CreateModel(
            name='AdServerLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_notes', models.TextField()),
                ('boostr_deal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consvc_shepherd.boostrdeal')),
            ],
        ),
        migrations.CreateModel(
            name='AdsBudgetForecast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField(default=datetime.date.today, verbose_name='Month & Year')),
                ('forecast', models.IntegerField(default=10)),
                ('country', models.ForeignKey(default=consvc_shepherd.models.Country.get_default_country, on_delete=django.db.models.deletion.CASCADE, to='consvc_shepherd.country')),
            ],
            options={
                'ordering': ['month', 'country__code'],
            },
        ),
        migrations.CreateModel(
            name='AdProductBudget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField()),
                ('budget', models.IntegerField()),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consvc_shepherd.adproduct')),
            ],
        ),
    ]