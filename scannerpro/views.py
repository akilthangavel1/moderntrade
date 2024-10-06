from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import StreamingHttpResponse

from .models import TickerBase, AccessToken
from .histdata import fetch_ohlc_data, process_ohlc_data, calculate_changes

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import json
import time




def fetch_tickers_for_scanner(request):
    tickers = TickerBase.objects.all().values('ticker_name', 'ticker_sector', 'ticker_sub_sector', 'ticker_market_cap')
    tickers_json = json.dumps(list(tickers))  # Convert QuerySet to list and then to JSON
    return render(request, "scannerhome.html", {'tickers': tickers_json})


def show_homepage(request):
    return render(request, "homepage.html", {})


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
    return "NSE:" + symbol + "24OCTFUT"


def generate_event_stream():
    while True:
        ticker_details = TickerBase.objects.all()
        ticker_list = []
        
        for ticker in ticker_details:
            from_date = (datetime.now() - timedelta(days=31)).strftime("%d/%m/%Y")
            to_date = datetime.now().strftime("%d/%m/%Y")
            symbol = format_symbol(ticker.ticker_symbol)
            resolution = "D"
            client_id = "MMKQTWNJH3-100"
            access_token = get_access_token()
            ohlc_daily_data = fetch_ohlc_data(symbol, resolution, from_date, to_date, client_id, access_token)
            processed_daily_ohlc = process_ohlc_data(ohlc_daily_data)
            
            if process_ohlc_data:
                latest_close, daily_change, weekly_change = calculate_changes(processed_daily_ohlc)
                previous_day_open = processed_daily_ohlc.iloc[-2]['open']
                previous_day_high = processed_daily_ohlc.iloc[-2]['high']
                previous_day_low = processed_daily_ohlc.iloc[-2]['low']
                previous_day_close = processed_daily_ohlc.iloc[-2]['close']
                latest_open = processed_daily_ohlc.iloc[-1]['open']
                latest_high = processed_daily_ohlc.iloc[-1]['high']
                latest_low = processed_daily_ohlc.iloc[-1]['low']
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
        
        if ticker_list:
            yield f"data: {json.dumps(ticker_list)}\n\n"
        else:
            yield f"data: No data available\n\n"
        
        time.sleep(20)


def sse_event_view(request):
    response = StreamingHttpResponse(generate_event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response






