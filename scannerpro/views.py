from django.conf import settings
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import TickerBase



def get_intraday_data(symbol, interval='1m'):
    """
    Fetches intraday stock data for a given symbol using yfinance.
    """
    end_time = datetime.now()
    start_time = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    try:
        df = yf.download(symbol, start=start_time, end=end_time, interval=interval)
        
        if not df.empty:
            df.reset_index(inplace=True)
            df.rename(columns={df.columns[0]: 'Datetime'}, inplace=True)
            df['Datetime'] = pd.to_datetime(df['Datetime'])  # Ensure Datetime is of datetime type
            df['Datetime'] = df['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Calculate indicators
            df = calculate_ema(df)
            df = calculate_atr(df)
            df = calculate_supertrend(df)
            df = df[150:]
            
            # Round numerical fields to 2 decimal points
            numerical_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'EMA20', 'EMA50', 'ATR', 'Supertrend']
            df[numerical_columns] = df[numerical_columns].round(2)
            
            # Return the data as a list of dictionaries
            return df.to_dict('records')
        else:
            return {'error': 'No data available for the given parameters'}
    
    except Exception as e:
        return {'error': 'Failed to fetch data', 'details': str(e)}


def calculate_ema(df, span1=20, span2=50):
    """
    Calculates Exponential Moving Averages (EMA) for given spans.
    """
    df['EMA20'] = df['Close'].ewm(span=span1, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=span2, adjust=False).mean()
    return df


def calculate_atr(df, window=14):
    """
    Calculates the Average True Range (ATR) indicator.
    """
    df['TR'] = np.maximum(df['High'] - df['Low'], 
                          np.maximum(abs(df['High'] - df['Close'].shift()), 
                                     abs(df['Low'] - df['Close'].shift())))
    df['ATR'] = df['TR'].rolling(window=window).mean()
    return df

def calculate_supertrend(df, multiplier=2):
    """
    Calculates the Supertrend indicator.
    """
    df['Upper Basic'] = (df['High'] + df['Low']) / 2 + (multiplier * df['ATR'])
    df['Lower Basic'] = (df['High'] + df['Low']) / 2 - (multiplier * df['ATR'])
    
    df['Supertrend'] = np.nan
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Upper Basic'].iloc[i-1]:
            df.loc[df.index[i], 'Supertrend'] = df['Lower Basic'].iloc[i]
        elif df['Close'].iloc[i] < df['Lower Basic'].iloc[i-1]:
            df.loc[df.index[i], 'Supertrend'] = df['Upper Basic'].iloc[i]
        else:
            df.loc[df.index[i], 'Supertrend'] = df['Supertrend'].iloc[i-1]

    df['Supertrend'] = df['Supertrend'].fillna(df['Lower Basic'])  # Fill NaN values in Supertrend
    return df

def scannerhome(request):
    symbol = 'RELIANCE.NS'
    data = get_intraday_data(symbol)
    
 # Debug statement to check data format
    
    if isinstance(data, dict) and 'error' in data:
        context = data
    else:
        context = {
            'data': data,
            'symbol': symbol  # Add symbol to context for template use
        }
    
    return render(request, "scannerhome.html", context)


def homepage(request):
    return render(request, "homepage.html", {})


def ticker_create(request):
    if request.method == 'POST':
        ticker_name = request.POST.get('ticker_name')
        ticker_symbol = request.POST.get('ticker_symbol')
        ticker_sector = request.POST.get('ticker_sector')
        ticker_market_cap = request.POST.get('ticker_market_cap')
        
        # Create and save the new ticker
        TickerBase.objects.create(
            ticker_name=ticker_name,
            ticker_symbol=ticker_symbol,
            ticker_sector=ticker_sector,
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
        ticker.ticker_sector = request.POST.get('ticker_sector')
        ticker.ticker_market_cap = request.POST.get('ticker_market_cap')

        ticker.save()
        
        return redirect('ticker_list')
    
    return render(request, 'ticker_update.html', {'ticker': ticker})


def ticker_delete(request, pk):
    ticker = get_object_or_404(TickerBase, pk=pk)
    
    if request.method == 'POST':
        ticker.delete()
        return redirect('ticker_list')
    
    return render(request, 'ticker_delete.html', {'ticker': ticker})