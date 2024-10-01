from django.conf import settings
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import TickerBase
import json



def scannerhome(request):
    tickers = TickerBase.objects.all().values('ticker_name', 'ticker_sector', 'ticker_sub_sector', 'ticker_market_cap')
    tickers_json = json.dumps(list(tickers))  # Convert QuerySet to list and then to JSON
    return render(request, "scannerhome.html", {'tickers': tickers_json})


def homepage(request):
    return render(request, "homepage.html", {})


def ticker_create(request):
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
        
        return redirect('ticker_list')
    
    return render(request, 'ticker_create.html')

def ticker_list(request):
    tickers = TickerBase.objects.all()
    return render(request, 'ticker_list.html', {'tickers': tickers})


def ticker_update(request, pk):
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
        
        return redirect('ticker_list')
    
    return render(request, 'ticker_update.html', {'ticker': ticker})


def ticker_delete(request, pk):
    ticker = get_object_or_404(TickerBase, pk=pk)
    if request.method == 'POST':
        ticker.delete()
        return redirect('ticker_list')
    return render(request, 'ticker_delete.html', {'ticker': ticker})


from .models import AccessToken

def get_access_token_value():
    try:
        token_instance = AccessToken.objects.get()  # This assumes only one instance exists
        return token_instance.value
    except AccessToken.DoesNotExist:
        return None  # Handle the case where no token exists
    except AccessToken.MultipleObjectsReturned:
        return None  # Shouldn't happen, but just in case

def process_symbol(symbol):
    return "NSE:"+symbol+"24OCTFUT"


import time
import json
from django.http import StreamingHttpResponse
from .models import TickerBase
from .histdata import fetch_ohlc_data, process_ohlc_data, calculate_changes


def event_stream():
    while True:
        ticker_details = TickerBase.objects.all()
        ticker_list = []
        for ticker in ticker_details:
            from_date = (datetime.now() - timedelta(days=31)).strftime("%d/%m/%Y")
            to_date = datetime.now().strftime("%d/%m/%Y")
            symbol = process_symbol(ticker.ticker_symbol) 
            resolution = "D"
            client_id = "MMKQTWNJH3-100"
            access_token = get_access_token_value()
            ohlc_daily_data = fetch_ohlc_data(symbol, resolution, from_date, to_date, client_id, access_token)
            # print(ohlc_daily_data)
            processed_daily_ohlc = process_ohlc_data(ohlc_daily_data)
            if process_ohlc_data:
                latest_close, daily_change, weekly_change = calculate_changes(processed_daily_ohlc)
            
            ticker_data = {
                "name": ticker.ticker_name,
                "symbol": ticker.ticker_symbol,
                "sector": ticker.ticker_sector,
                "sub_sector": ticker.ticker_sub_sector,
                "market_cap": ticker.ticker_market_cap,
                "ltp": latest_close,
                "daily_change": daily_change,
                "weekly_change": weekly_change
            }
            
            ticker_list.append(ticker_data)
        if ticker_list:
            yield f"data: {json.dumps(ticker_list)}\n\n"
        else:
            yield f"data: No data available\n\n"

        time.sleep(20)

def sse_view(request):
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response