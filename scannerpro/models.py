from django.db import models

class TickerBase(models.Model):
    ticker_name = models.CharField(max_length=200, unique=True)
    ticker_symbol = models.CharField(max_length=20, unique=True)
    ticker_sector = models.CharField(max_length=100)
    ticker_sub_sector = models.CharField(max_length=100, blank=True, null=True)
    ticker_market_cap = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.ticker_symbol} ({self.ticker_sector}) - {self.ticker_market_cap}"
