# Generated by Django 4.2.14 on 2024-08-05 20:18

import consvc_shepherd.models
import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('consvc_shepherd', '0008_boostrdeal_boostrproduct_boostrdealproduct_and_more'),
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
            name='AdProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField()),
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
        migrations.AlterField(
            model_name='boostrdealproduct',
            name='month',
            field=models.DateField(),
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