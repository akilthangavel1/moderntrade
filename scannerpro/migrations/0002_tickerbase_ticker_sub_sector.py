# Generated by Django 5.0.7 on 2024-08-21 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scannerpro', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickerbase',
            name='ticker_sub_sector',
            field=models.CharField(default=True, max_length=20),
            preserve_default=False,
        ),
    ]
