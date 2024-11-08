# scannerpro/tasks.py
from celery import shared_task
from django.apps import apps
from django.db import connection

def insert_wc_data(ticker_symbol, last_traded_time, ltp):
    wc_table_name = f"{ticker_symbol.lower()}_wc"
    
    insert_query = f"""
    INSERT INTO "{wc_table_name}" (timestamp, ltp)
    VALUES (to_timestamp(%s), %s)
    """
    
    with connection.cursor() as cursor:
        cursor.execute(insert_query, [last_traded_time, ltp])



@shared_task
def process_stock_data(message):
    try:
        # Parse and extract data from the message
        data = message
        symbol = data.get('symbol')
        ltp = data.get('ltp')
        last_traded_time = data.get('last_traded_time')
        if not symbol or not ltp:
            print("Symbol or LTP missing in message.")
            return

        print(f"Original Symbol: {symbol}")
        # Extract the model name by removing "NSE:" and "-EQ"
        symbol = symbol.replace("NSE:", "").replace("-EQ", "")
        print(f"Derived Model Name: {symbol}")
        wc_table_name = f"{symbol.lower()}_wc"
        insert_query = f"""
        INSERT INTO "{wc_table_name}" (timestamp, ltp)
        VALUES (to_timestamp(%s), %s)
        """
        
        with connection.cursor() as cursor:
            cursor.execute(insert_query, [last_traded_time, ltp])

        # # Dynamically get the model from the app registry
        # try:
        #     model = apps.get_model('scannerpro', result)
        # except LookupError:
        #     print(f"Model '{result}' not found in 'scannerpro' app.")
        #     return

        # # Create an instance of the model
        # model.objects.create(symbol=symbol, ltp=ltp)
        # print(f"Successfully saved data for {symbol}.")

    except Exception as e:
        print(f"Error processing message: {e}")
