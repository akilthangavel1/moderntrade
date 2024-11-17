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
        data = message
        symbol = data.get('symbol')
        ltp = data.get('ltp')
        last_traded_time = data.get('last_traded_time')
        if not symbol or not ltp:
            print("Symbol or LTP missing in message.")
            return

        print(f"Original Symbol: {symbol}")
        # Extract the model name by removing "NSE:" and "-EQ"
        symbol = symbol.replace("NSE:", "").replace("-EQ", "").replace("24NOVFUT", "")
        print(f"Derived Model Name: {symbol}")
        wc_table_name = f"{symbol.lower()}_future_websocket_data"
        insert_query = f"""
        INSERT INTO "{wc_table_name}" (timestamp, ltp)
        VALUES (to_timestamp(%s), %s)
        """
        
        with connection.cursor() as cursor:
            cursor.execute(insert_query, [last_traded_time, ltp])

    except Exception as e:
        print(f"Error processing message: {e}")



from celery import shared_task

@shared_task
def update_ticker_data():
    print("Ticker data updated successfully!")