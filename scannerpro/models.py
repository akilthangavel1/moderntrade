from django.db import models, connection
import re
from django.core.exceptions import ValidationError

class TickerBase(models.Model):
    # Constants for market cap choices
    LARGE_CAP = 'Large Cap'
    MID_CAP = 'Mid Cap'
    SMALL_CAP = 'Small Cap'

    MARKET_CAP_CHOICES = [
        (LARGE_CAP, 'Large Cap'),
        (MID_CAP, 'Mid Cap'),
        (SMALL_CAP, 'Small Cap'),
    ]

    # Constants for sector choices
    AUTOMOBILE = 'Automobile'
    BANKING = 'Banking'
    CAPITAL_GOODS = 'Capital Goods'
    CEMENT = 'Cement'
    CHEMICALS = 'Chemicals'
    FINANCE = 'Finance'
    FMCG = 'FMCG'
    INDEX = 'Index'
    INFRASTRUCTURE = 'Infrastructure'
    MEDIA = 'Media'
    METALS = 'Metals'
    OIL_AND_GAS = 'Oil and Gas'
    PHARMA = 'Pharma'
    POWER = 'Power'
    REALTY = 'Realty'
    TECHNOLOGY = 'Technology'
    TELECOM = 'Telecom'
    TEXTILE = 'Textile'
    OTHERS = 'Others'

    SECTOR_CHOICES = [
        (AUTOMOBILE, 'Automobile'),
        (BANKING, 'Banking'),
        (CAPITAL_GOODS, 'Capital Goods'),
        (CEMENT, 'Cement'),
        (CHEMICALS, 'Chemicals'),
        (FINANCE, 'Finance'),
        (FMCG, 'FMCG'),
        (INDEX, 'Index'),
        (INFRASTRUCTURE, 'Infrastructure'),
        (MEDIA, 'Media'),
        (METALS, 'Metals'),
        (OIL_AND_GAS, 'Oil and Gas'),
        (PHARMA, 'Pharma'),
        (POWER, 'Power'),
        (REALTY, 'Realty'),
        (TECHNOLOGY, 'Technology'),
        (TELECOM, 'Telecom'),
        (TEXTILE, 'Textile'),
        (OTHERS, 'Others'),
    ]

    ticker_name = models.CharField(max_length=200, unique=True)
    ticker_symbol = models.CharField(max_length=20, unique=True)
    ticker_sector = models.CharField(
        max_length=50,
        choices=SECTOR_CHOICES,
        default=OTHERS,
    )
    ticker_sub_sector = models.CharField(max_length=100, blank=True, null=True)
    ticker_market_cap = models.CharField(
        max_length=20,
        choices=MARKET_CAP_CHOICES,
        default=LARGE_CAP,
    )

    def __str__(self):
        return f"{self.ticker_symbol} ({self.ticker_sector}) - {self.ticker_market_cap}"

    def save(self, *args, **kwargs):
        # Validate ticker symbol for table names
        if not re.match(r'^[a-zA-Z0-9_]+$', self.ticker_symbol):
            raise ValidationError("Ticker symbol contains invalid characters.")

        # Call the original save method to insert the TickerBase record
        super().save(*args, **kwargs)

        # Get the table name using ticker_symbol in lowercase
        table_name = self.ticker_symbol.lower()
        wc_table_name = f"{table_name}_wc"

        # SQL query to create the main table
        create_main_table_query = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            id SERIAL PRIMARY KEY,
            datetime TIMESTAMPTZ NOT NULL,
            open_price FLOAT NOT NULL,
            high_price FLOAT NOT NULL,
            low_price FLOAT NOT NULL,
            close_price FLOAT NOT NULL,
            volume BIGINT
        )
        """

        # SQL query to create the WebSocket data table
        create_wc_table_query = f"""
        CREATE TABLE IF NOT EXISTS "{wc_table_name}" (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL,
            ltp FLOAT NOT NULL
        )
        """

        # Execute the queries to create both tables
        with connection.cursor() as cursor:
            cursor.execute(create_main_table_query)
            cursor.execute(create_wc_table_query)


# models.py in your Django app (e.g., scannerpro/models.py)
from django.db import models
from django.core.exceptions import ValidationError

class AccessToken(models.Model):
    value = models.TextField()

    def save(self, *args, **kwargs):
        if not self.pk and AccessToken.objects.exists():
            raise ValidationError('Only one instance of SingleRecord is allowed.')
        return super(AccessToken, self).save(*args, **kwargs)

    def __str__(self):
        return self.value