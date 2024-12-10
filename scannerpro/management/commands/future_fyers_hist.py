from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from scannerpro.models import TickerBase
import time
from scannerpro.views import (
    future_format_symbol,
    get_access_token,
    fetch_ohlc_data,
    process_ohlc_data,
    data_exists,
    insert_data_into_historical_db
)

class Command(BaseCommand):
    help = "Updates historical OHLC data in the database for all tickers."

    def handle(self, *args, **options):
        ticker_details = TickerBase.objects.all()
        
        for ticker in ticker_details:
            try:
                self.stdout.write(self.style.SUCCESS(f"Processing ticker: {ticker.ticker_symbol}"))
                from_date = (datetime.now() - timedelta(days=14)).strftime("%d/%m/%Y")
                to_date = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
                print(ticker.ticker_symbol)
                symbol = future_format_symbol(ticker.ticker_symbol.upper())
                resolution = "1"
                client_id = "MMKQTWNJH3-100"
                access_token = get_access_token()
                print(symbol)
                ohlc_daily_data = fetch_ohlc_data(symbol, resolution, from_date, to_date, client_id, access_token)
                processed_daily_ohlc = process_ohlc_data(ohlc_daily_data)
                time.sleep(1)
                for _, row in processed_daily_ohlc.iterrows():
                    if not data_exists(ticker.ticker_symbol + "_future_historical_data", row.datetime):
                        insert_data_into_historical_db(
                            table_name= ticker.ticker_symbol + "_future_historical_data",
                            datetime_value=row.datetime,
                            open_price=row.open,
                            high_price=row.high,
                            low_price=row.low,
                            close_price=row.close,
                            volume=row.volume
                        )
                        # self.stdout.write(self.style.SUCCESS(f"Inserted data for {ticker.ticker_symbol} on {row.datetime}."))
                    else:
                        self.stdout.write(self.style.WARNING(f"Data for {ticker.ticker_symbol} on {row.datetime} already exists. Skipping."))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing ticker {ticker.ticker_symbol}: {e}"))
        
        self.stdout.write(self.style.SUCCESS("Data Inserted"))

