from django.core.management.base import BaseCommand
import pandas as pd
from scannerpro.models import TickerBase  # Replace 'myapp' with your app name

# class Command(BaseCommand):
#     help = 'Test command for argument passing'

#     def add_arguments(self, parser):
#         parser.add_argument('test_argument', type=str, help='A test argument')

#     def handle(self, *args, **kwargs):
#         print("Test Argument:", kwargs['test_argument'])
# python manage.py import_tickers test_value



# from django.core.management.base import BaseCommand
# import pandas as pd

# class Command(BaseCommand):
#     help = 'Read ticker data from an Excel file'

#     def add_arguments(self, parser):
#         parser.add_argument('file_path', type=str, help='The path to the Excel file to be imported')

#     def handle(self, *args, **kwargs):
#         file_path = kwargs['file_path']
#         self.stdout.write(self.style.WARNING(f'Reading file: {file_path}'))

#         try:
#             df = pd.read_excel(file_path)
#             self.stdout.write(self.style.SUCCESS(f'Successfully read the Excel file. Here is the data:\n{df.head()}'))
#         except FileNotFoundError:
#             self.stdout.write(self.style.ERROR('File not found. Please provide a valid file path.'))
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))


from django.core.management.base import BaseCommand
import pandas as pd
from scannerpro.models import TickerBase  # Replace 'myapp' with your app name

class Command(BaseCommand):
    help = 'Import ticker data from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the Excel file to be imported')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        self.stdout.write(self.style.WARNING(f'Reading file: {file_path}'))

        try:
            # Read the Excel file
            df = pd.read_excel(file_path)
            print(df.head())
            # Iterate over the rows in the DataFrame
            for index, row in df.iterrows():
                # Create a new TickerBase object for each row
                ticker_name=row['Company Name']       # Assuming these columns exist in the Excel file
                ticker_symbol=row['Descr.']           # Adjust column names as necessary
                ticker_sector=row['Sectors']
                ticker_sub_sector=row['Sub - Sector']
                ticker_market_cap=row['Large/Midcap/Small Cap'] if pd.notna(row['Large/Midcap/Small Cap']) else ''
                print(ticker_name, ticker_symbol, ticker_sector, ticker_sub_sector, ticker_market_cap)
                ticker = TickerBase(
                    ticker_name=ticker_name,         # Assuming these columns exist in the Excel file
                    ticker_symbol=ticker_symbol,             # Adjust column names as necessary
                    ticker_sector=ticker_sector,
                    ticker_sub_sector=ticker_sub_sector,
                    ticker_market_cap=ticker_market_cap,
                )
                
                print("@" * 40)
                ticker.save()
                print("#################")
            self.stdout.write(self.style.SUCCESS('Successfully imported ticker data into the database.'))
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('File not found. Please provide a valid file path.'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
