# scannerpro/management/commands/start_fyers_socket.py
from django.core.management.base import BaseCommand
from fyers_apiv3.FyersWebsocket import data_ws
from scannerpro.tasks import process_stock_data
from scannerpro.models import TickerBase, AccessToken
from scannerpro.views import future_format_symbol


class Command(BaseCommand):
    help = 'Start Fyers WebSocket connection and listen for real-time data'

    def handle(self, *args, **kwargs):
        def onmessage(message):
            print(message)
            process_stock_data.delay(message)

        def onerror(message):
            print("Error:", message)

        def onclose(message):
            print("Connection closed:", message)
            

        def onopen():
            data_type = "SymbolUpdate"
            symbols = list(TickerBase.objects.values_list('ticker_symbol', flat=True))
            fyers_symbols = [(future_format_symbol(stock)).upper() for stock in symbols]
            fyers.subscribe(symbols=fyers_symbols, data_type=data_type)
            fyers.keep_running()

        access_token = AccessToken.objects.get()  
        access_token = access_token.value 
        fyers = data_ws.FyersDataSocket(
            access_token=access_token,
            log_path="",
            litemode=False,
            write_to_file=False,
            reconnect=True,
            on_connect=onopen,
            on_close=onclose,
            on_error=onerror,
            on_message=onmessage
        )
        fyers.connect()
