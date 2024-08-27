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