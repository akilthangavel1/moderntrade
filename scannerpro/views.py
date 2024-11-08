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

def get_hist_data_raw(ticker_symbol):
    if not ticker_symbol:
        return JsonResponse({'error': 'Ticker symbol not provided'}, status=400)
    
    table_name = ticker_symbol.lower()
    query = f"SELECT * FROM {table_name}"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            ticker_data = [dict(zip(columns, row)) for row in rows]
            return ticker_data
            # return JsonResponse(ticker_data, safe=False)
    except Exception as e:
        return None
    

def get_ticker_data_raw(ticker_symbol):
    if not ticker_symbol:
        return JsonResponse({'error': 'Ticker symbol not provided'}, status=400)
    
    table_name = ticker_symbol.lower() + "_wc"
    query = f"SELECT * FROM {table_name}"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            ticker_data = [dict(zip(columns, row)) for row in rows]
            return ticker_data
            # return JsonResponse(ticker_data, safe=False)
    except Exception as e:
        print(e)
        return None

import asyncio
import pandas as pd
from django.http import StreamingHttpResponse
from asgiref.sync import sync_to_async

@sync_to_async
def get_tickers():
    return list(TickerBase.objects.all())

@sync_to_async
def get_hist_data(symbol):
    return get_hist_data_raw(symbol)

@sync_to_async
def get_tick_data(symbol):
    return get_ticker_data_raw(symbol)

async def generate_event_stream():
    while True:
        try:
            tickers = await get_tickers()  # Use async call to retrieve tickers
            ticker_list = []
            for ticker in tickers:
                try:
                    hist_data = await get_hist_data(ticker.ticker_symbol)
                    tick_data = await get_tick_data(ticker.ticker_symbol)
                    hist_df = pd.DataFrame(hist_data).drop('id', axis=1)
                    hist_df.rename(columns={
                        'open_price': 'open',
                        'high_price': 'high',
                        'low_price': 'low',
                        'close_price': 'close'
                    }, inplace=True)
                    hist_df.set_index('datetime', inplace=True)

                    tick_data = await get_tick_data(ticker.ticker_symbol)  # Use the async version to get tick data
                    tick_df = pd.DataFrame(tick_data)
                    tick_df['timestamp'] = tick_df['timestamp'].dt.floor('min')
                    tick_ohlc_df = tick_df.groupby('timestamp').agg(
                        open=('ltp', 'first'),
                        high=('ltp', 'max'),
                        low=('ltp', 'min'),
                        close=('ltp', 'last')
                    ).reset_index()
                    tick_ohlc_df['volume'] = 0
                    tick_ohlc_df.set_index('timestamp', inplace=True)
                    tick_ohlc_df.index.name = 'datetime'

                    hist_df.reset_index(inplace=True)
                    tick_ohlc_df.reset_index(inplace=True)
                    df = pd.concat([hist_df, tick_ohlc_df], ignore_index=True)
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df.set_index('datetime', inplace=True)

                    # Resample to daily timeframe
                    daily_df = df.resample('D').agg({
                        'open': 'first',
                        'high': 'max',
                        'low': 'min',
                        'close': 'last',
                        'volume': 'sum'
                    }).dropna()  # Drop days without data
                    # Calculate changes
                    daily_df = daily_df.reset_index()
                    latest_close, daily_change, weekly_change = calculate_changes(daily_df)
                    previous_day_open = daily_df.iloc[-2]['open']
                    previous_day_high = daily_df.iloc[-2]['high']
                    previous_day_low = daily_df.iloc[-2]['low']
                    previous_day_close = daily_df.iloc[-2]['close']
                    latest_open = daily_df.iloc[-1]['open']
                    latest_high = daily_df.iloc[-1]['high']
                    latest_low = daily_df.iloc[-1]['low']

                    # Prepare ticker data dictionary
                    ticker_data = {
                        "name": ticker.ticker_name,
                        "symbol": ticker.ticker_symbol,
                        "sector": ticker.ticker_sector,
                        "sub_sector": ticker.ticker_sub_sector,
                        "market_cap": ticker.ticker_market_cap,
                        "ltp": latest_close,
                        "daily_change": daily_change,
                        "weekly_change": weekly_change,
                        "previous_day_open": previous_day_open,
                        "previous_day_high": previous_day_high,
                        "previous_day_low": previous_day_low,
                        "previous_day_close": previous_day_close,
                        "latest_open": latest_open,
                        "latest_high": latest_high,
                        "latest_low": latest_low,
                    }

                    ticker_list.append(ticker_data)
                except Exception as e:
                    print(f"Error processing {ticker.ticker_symbol}: {str(e)}")

            yield f"data: {json.dumps(ticker_list)}\n\n"
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            yield f"data: Exception occurred: {str(e)}\n\n"
        await asyncio.sleep(1)  # Pause before the next cycle


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