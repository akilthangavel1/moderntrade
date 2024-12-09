from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from asgiref.sync import sync_to_async
from django.db import connection
import pandas as pd
import json
import asyncio
from .models import TickerBase, AccessToken
from .histdata import calculate_changes

# Synchronous Function Wrappers
@sync_to_async
def fetch_all_tickers():
    return list(TickerBase.objects.all())

@sync_to_async
def fetch_historical_data_raw(ticker_symbol):
    table_name = ticker_symbol.lower() + "_future_historical_data"
    query = f"SELECT * FROM {table_name}"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None

@sync_to_async
def fetch_ticker_data_raw(ticker_symbol):
    table_name = ticker_symbol.lower() + "_future_websocket_data"
    query = f"SELECT * FROM {table_name}"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"Error fetching ticker data: {e}")
        return None

# SSE Stream Function
async def generate_event_stream():
    while True:
        
        try:
            tickers = await fetch_all_tickers()
            ticker_list = []
            
            for ticker in tickers:
                try:
                    hist_data = await fetch_historical_data_raw(ticker.ticker_symbol)
                    tick_data = await fetch_ticker_data_raw(ticker.ticker_symbol)
                    if hist_data and tick_data:
                        hist_df = pd.DataFrame(hist_data).drop('id', axis=1)
                        hist_df.rename(columns={
                            'open_price': 'open',
                            'high_price': 'high',
                            'low_price': 'low',
                            'close_price': 'close'
                        }, inplace=True)
                        hist_df.set_index('datetime', inplace=True)
                        tick_df = pd.DataFrame(tick_data)
                        tick_df['timestamp'] = pd.to_datetime(tick_df['timestamp'])
                        tick_df = tick_df.groupby(tick_df['timestamp'].dt.floor('min')).agg(
                            open=('ltp', 'first'),
                            high=('ltp', 'max'),
                            low=('ltp', 'min'),
                            close=('ltp', 'last')
                        ).reset_index()
                        tick_df.set_index('timestamp', inplace=True)
                        tick_df.index.name = 'datetime'
                        combined_df = pd.concat([hist_df, tick_df]).sort_index()
                        daily_df = combined_df.resample('D').agg({
                            'open': 'first',
                            'high': 'max',
                            'low': 'min',
                            'close': 'last'
                        }).dropna()
                        print(daily_df)
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
                    print(f"Error processing ticker {ticker.ticker_symbol}: {e}")

            # Send data as SSE event
            yield f"data: {json.dumps(ticker_list)}\n\n"
        except Exception as e:
            print(f"Exception in event stream: {e}")
            yield f"data: Exception occurred: {str(e)}\n\n"

        # Wait before sending the next update
        await asyncio.sleep(1)

# SSE View
async def sse_event_view(request):
    response = StreamingHttpResponse(generate_event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response

# Basic Views
def show_homepage(request):
    return render(request, "homepage.html")

def list_tickers(request):
    tickers = TickerBase.objects.all()
    return render(request, 'ticker_list.html', {'tickers': tickers})

def create_ticker(request):
    if request.method == 'POST':
        ticker_name = request.POST.get('ticker_name')
        ticker_symbol = request.POST.get('ticker_symbol')
        ticker_sector = request.POST.get('ticker_sector')
        ticker_sub_sector = request.POST.get('ticker_sub_sector')
        ticker_market_cap = request.POST.get('ticker_market_cap')

        TickerBase.objects.create(
            ticker_name=ticker_name,
            ticker_symbol=ticker_symbol,
            ticker_sector=ticker_sector,
            ticker_sub_sector=ticker_sub_sector,
            ticker_market_cap=ticker_market_cap
        )
        return redirect('list_tickers')

    return render(request, 'ticker_create.html')

def fetch_tickers_for_scanner(request):
    tickers = TickerBase.objects.all().values('ticker_symbol', 'ticker_name')
    tickers_list = list(tickers)  # Convert queryset to list
    return JsonResponse(tickers_list, safe=False)  # Return as JSON

def dummy_homepage(request):
    return render(request, "dummypage.html", {})


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


def api_home(request):
    return render(request, 'dummy2.html', {})

def dynamicscanner(request):
    return render(request, 'index.html', {})

def option_screen(request):
    return render(request, 'optionscr.html', {})

@sync_to_async
def get_access_token():
    try:
        token_instance = AccessToken.objects.get() 
        return token_instance.value
    except AccessToken.DoesNotExist:
        return None  
    except AccessToken.MultipleObjectsReturned:
        return None  
    


def insert_data_into_historical_db(table_name, datetime_value, open_price, high_price, low_price, close_price, volume):
    table_name = table_name.lower()
    print(table_name)
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