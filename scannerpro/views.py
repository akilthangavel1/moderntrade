from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import StreamingHttpResponse
from django.http import HttpResponse
from django.apps import apps
from .models import TickerBase, AccessToken
from .histdata import fetch_ohlc_data, process_ohlc_data, calculate_changes, calculate_weekly_ohlc, test_week_data
from django.apps import apps
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import json
import time
from django.db import connection
from datetime import date





def fetch_tickers_for_scanner(request):
    tickers = TickerBase.objects.all().values('ticker_name', 'ticker_sector', 'ticker_sub_sector', 'ticker_market_cap')
    tickers_json = json.dumps(list(tickers))  # Convert QuerySet to list and then to JSON
    return render(request, "scannerhome.html", {'tickers': tickers_json})


def show_homepage(request):
    return render(request, "homepage.html", {})

def dummy_homepage(request):
    return render(request, "dummypage.html", {})

def create_ticker(request):
    if request.method == 'POST':
        ticker_name = request.POST.get('ticker_name')
        ticker_symbol = request.POST.get('ticker_symbol')
        ticker_sector = request.POST.get('ticker_sector')
        ticker_sub_sector = request.POST.get('ticker_sub_sector')  # New field
        ticker_market_cap = request.POST.get('ticker_market_cap')
        
        # Create and save the new ticker
        TickerBase.objects.create(
            ticker_name=ticker_name,
            ticker_symbol=ticker_symbol,
            ticker_sector=ticker_sector,
            ticker_sub_sector=ticker_sub_sector,  # New field
            ticker_market_cap=ticker_market_cap
        )
        
        return redirect('list_tickers')
    
    return render(request, 'ticker_create.html')


def list_tickers(request):
    tickers = TickerBase.objects.all()
    return render(request, 'ticker_list.html', {'tickers': tickers})


def update_ticker(request, pk):
    ticker = get_object_or_404(TickerBase, pk=pk)
    
    if request.method == 'POST':
        ticker.ticker_name = request.POST.get('ticker_name')
        ticker.ticker_symbol = request.POST.get('ticker_symbol')
        ticker_sector = request.POST.get('ticker_sector')
        ticker_sub_sector = request.POST.get('ticker_sub_sector')  # New field
        ticker_market_cap = request.POST.get('ticker_market_cap')

        ticker.ticker_sector = ticker_sector
        ticker.ticker_sub_sector = ticker_sub_sector  # New field
        ticker.ticker_market_cap = ticker_market_cap

        ticker.save()
        
        return redirect('list_tickers')
    
    return render(request, 'ticker_update.html', {'ticker': ticker})


def delete_ticker(request, pk):
    ticker = get_object_or_404(TickerBase, pk=pk)
    if request.method == 'POST':
        ticker.delete()
        return redirect('list_tickers')
    return render(request, 'ticker_delete.html', {'ticker': ticker})


def get_access_token():
    try:
        token_instance = AccessToken.objects.get()  # This assumes only one instance exists
        return token_instance.value
    except AccessToken.DoesNotExist:
        return None  # Handle the case where no token exists
    except AccessToken.MultipleObjectsReturned:
        return None  # Shouldn't happen, but just in case


def format_symbol(symbol):
    return "NSE:" + symbol + "24NOVFUT"


import asyncio

# Modify this function to be asynchronous
async def generate_event_stream():
    while True:
        ticker_list = []
        try:
            ticker_details = TickerBase.objects.all()
            
            for ticker in ticker_details:
                from_date = (datetime.now() - timedelta(days=31)).strftime("%d/%m/%Y")
                to_date = datetime.now().strftime("%d/%m/%Y")
                symbol = format_symbol(ticker.ticker_symbol)
                resolution = "D"
                client_id = "MMKQTWNJH3-100"
                access_token = get_access_token()
                ohlc_daily_data = fetch_ohlc_data(symbol, resolution, from_date, to_date, client_id, access_token)
                processed_daily_ohlc = process_ohlc_data(ohlc_daily_data)
                weekly_df = test_week_data(processed_daily_ohlc)
                print(weekly_df)
                # Uncomment and process as needed
                # latest_close, daily_change, weekly_change = calculate_changes(processed_daily_ohlc)
                # Prepare ticker data dictionary and append to ticker_list here

        except Exception as e:
            print(f"Exception occurred: {str(e)}")
        
        # Yield the data if available, or indicate no data
        if ticker_list:
            yield f"data: {json.dumps(ticker_list)}\n\n"
        else:
            yield f"data: No data available\n\n"
        
        # Use asyncio.sleep to avoid blocking
        await asyncio.sleep(20)

# Convert sse_event_view to async to handle async generator
async def sse_event_view(request):
    response = StreamingHttpResponse(generate_event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response



def insert_data_into_ticker_table(ticker_symbol, datetime_value, open_price, high_price, low_price, close_price, volume):
    table_name = ticker_symbol.lower()

    insert_query = f"""
    INSERT INTO "{table_name}" (datetime, open_price, high_price, low_price, close_price, volume)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(insert_query, [datetime_value, open_price, high_price, low_price, close_price, volume])
            print(f"Data inserted successfully into {table_name} table.")
    except Exception as e:
        print(f"Error inserting data into {table_name} table: {e}")



# def histdata_update_db(request):
#     ticker_details = TickerBase.objects.all()
#     for ticker in ticker_details:
#         print(ticker.ticker_symbol)
#         from_date = (datetime.now() - timedelta(days=28)).strftime("%d/%m/%Y")
#         to_date = datetime.now().strftime("%d/%m/%Y")
#         symbol = format_symbol(ticker.ticker_symbol)
#         resolution = "D"
#         client_id = "MMKQTWNJH3-100"
#         access_token = get_access_token()
#         ohlc_daily_data = fetch_ohlc_data(symbol, resolution, from_date, to_date, client_id, access_token)
#         processed_daily_ohlc = process_ohlc_data(ohlc_daily_data)
#         print(processed_daily_ohlc)
#         for index, row in processed_daily_ohlc.iterrows():
#             print(row.datetime, row.open)
#             insert_data_into_ticker_table(
#                 ticker_symbol=ticker.ticker_symbol, 
#                 datetime_value=datetime(2024, 11, 6, 10, 30),  # Example datetime
#                 open_price=row.open, 
#                 high_price=row.high, 
#                 low_price=row.low, 
#                 close_price=row.close, 
#                 volume=row.volume
#             )
#     return HttpResponse("Data Inserted")




def data_exists(ticker_symbol, datetime_value):
    try:
        table_name = ticker_symbol.lower()
        query = f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE datetime = %s)"
        with connection.cursor() as cursor:
            cursor.execute(query, [datetime_value])
            return bool(cursor.fetchone()[0])
    except Exception as e:
        print("An error occurred:", e)
        return False
    

def histdata_update_db(request):
    ticker_details = TickerBase.objects.all()
    for ticker in ticker_details:
        try:
            print(f"Processing ticker: {ticker.ticker_symbol}")
            from_date = (datetime.now() - timedelta(days=28)).strftime("%d/%m/%Y")
            to_date = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
            symbol = format_symbol(ticker.ticker_symbol)
            resolution = "1"
            client_id = "MMKQTWNJH3-100"
            access_token = get_access_token()
            ohlc_daily_data = fetch_ohlc_data(symbol, resolution, from_date, to_date, client_id, access_token)
            print(ohlc_daily_data)
            processed_daily_ohlc = process_ohlc_data(ohlc_daily_data)
            print(processed_daily_ohlc)
            for _, row in processed_daily_ohlc.iterrows():
                if not data_exists(ticker.ticker_symbol, row.datetime):
                    print(row.datetime)
                    insert_data_into_ticker_table(
                        ticker_symbol=ticker.ticker_symbol, 
                        datetime_value=row.datetime,
                        open_price=row.open, 
                        high_price=row.high, 
                        low_price=row.low, 
                        close_price=row.close, 
                        volume=row.volume   
                    )
                    print(f"Inserted data for {ticker.ticker_symbol} on {row.datetime}.")
                else:
                    print(f"Data for {ticker.ticker_symbol} on {row.datetime} already exists. Skipping.")
        
        except Exception as e:
            print(f"Error processing ticker {ticker.ticker_symbol}: {e}")
    
    return HttpResponse("Data Inserted")







from django.http import JsonResponse
def get_ticker_data(request):
    ticker_symbol = request.GET.get('ticker_symbol')
    if not ticker_symbol:
        return JsonResponse({'error': 'Ticker symbol not provided'}, status=400)
    
    table_name = ticker_symbol.lower()
    query = f"SELECT * FROM {table_name} ORDER BY datetime DESC LIMIT 100"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            ticker_data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(ticker_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def fetch_tickers_for_scanner(request):
    tickers = TickerBase.objects.all().values('ticker_symbol', 'ticker_name')
    tickers_list = list(tickers)  # Convert queryset to list
    return JsonResponse(tickers_list, safe=False)  # Return as JSON


def api_home(request):
    return render(request, 'dummy2.html', {})