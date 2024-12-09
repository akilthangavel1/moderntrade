from django.core.management.base import BaseCommand
from django.db import connection
from scannerpro.models import TickerBase

class Command(BaseCommand):
    help = "Deletes all records from tables named <ticker_symbol>_future_historical_data."

    def handle(self, *args, **options):
        ticker_details = TickerBase.objects.all()

        for ticker in ticker_details:
            table_name = f"{ticker.ticker_symbol.lower()}_future_historical_data"
            delete_query = f'DELETE FROM "{table_name}"'
            
            try:
                with connection.cursor() as cursor:
                    cursor.execute(delete_query)
                    self.stdout.write(self.style.SUCCESS(f"Deleted all records from table {table_name}."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error deleting records from table {table_name}: {e}"))

        self.stdout.write(self.style.SUCCESS("All specified records have been deleted."))
