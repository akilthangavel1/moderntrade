import pandas as pd
from django.core.management.base import BaseCommand
from scannerpro.models import TickerBase
import re  # Regular expression module to sanitize input

class Command(BaseCommand):
    help = 'Import processed ticker data into the TickerBase table'

    def handle(self, *args, **kwargs):
        # Path to the processed Excel file
        file_path = "/home/akil/Desktop/Upwork/Trading system - Hari/moderntrade/blocks/data/Processed_Futures.xlsx"
        
        try:
            # Read the processed Excel file into a pandas DataFrame
            data = pd.read_excel(file_path)

            # Loop through each row in the DataFrame and insert into the TickerBase table
            for index, row in data.iterrows():
                ticker_name = row['Processed_ScripName']
                print(ticker_name)
                print("############################################")
                
                # Sanitize ticker_symbol by removing non-alphanumeric characters and underscores
                ticker_symbol = re.sub(r'[^a-zA-Z0-9_]', '', ticker_name)  # Keep only alphanumeric and underscore
                
                # Ensure that the ticker_symbol is not empty after sanitization
                if not ticker_symbol:
                    ticker_symbol = 'UNKNOWN'  # Use a default value if the sanitized symbol is empty

                # Check if ticker_name already exists
                if not TickerBase.objects.filter(ticker_name=ticker_name).exists():
                    # Create a TickerBase object if it does not exist
                    TickerBase.objects.create(
                        ticker_name=ticker_name,
                        ticker_symbol=ticker_symbol,  # Use sanitized ticker symbol
                        ticker_sector='Others',  # Default sector if not available in the file
                        ticker_sub_sector=None,  # Adjust if sub-sector data is available
                        ticker_market_cap='Large Cap',  # Default market cap
                    )
                else:
                    print(f"Ticker '{ticker_name}' already exists, skipping.")

            self.stdout.write(self.style.SUCCESS('Successfully imported ticker data.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
