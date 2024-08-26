from django.db import models

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
