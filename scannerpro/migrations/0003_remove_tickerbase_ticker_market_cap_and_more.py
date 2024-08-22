# Generated by Django 5.1 on 2024-08-22 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scannerpro', '0002_tickerbase_ticker_sub_sector'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tickerbase',
            name='ticker_market_cap',
        ),
        migrations.AddField(
            model_name='tickerbase',
            name='ticker_market_size',
            field=models.CharField(default=True, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tickerbase',
            name='ticker_name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='tickerbase',
            name='ticker_sector',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tickerbase',
            name='ticker_sub_sector',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tickerbase',
            name='ticker_symbol',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
