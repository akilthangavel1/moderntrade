from django.shortcuts import render
import requests
from django.conf import settings
import pandas as pd
import numpy as np

def get_daily_time_series(api_key, symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()

        if 'Time Series (Daily)' in data:
            time_series = data['Time Series (Daily)']
            formatted_data = [
                {
                    'Date': date,
                    'Open': values['1. open'],
                    'High': values['2. high'],
                    'Low': values['3. low'],
                    'Close': values['4. close'],
                    'Volume': values['5. volume'],
                }
                for date, values in time_series.items()
            ]
            
            df = pd.DataFrame(formatted_data)

            # Convert relevant columns to numeric types
            for column in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[column] = pd.to_numeric(df[column])
                
            # Set 'Date' as the index
            df.set_index('Date', inplace=True)

            # Calculate EMA
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            
            # Calculate ATR
            df['TR'] = np.maximum(df['High'] - df['Low'], 
                                  np.maximum(abs(df['High'] - df['Close'].shift()), 
                                             abs(df['Low'] - df['Close'].shift())))
            df['ATR'] = df['TR'].rolling(window=14).mean()

            # Calculate Supertrend
            df['Upper Basic'] = (df['High'] + df['Low']) / 2 + (2 * df['ATR'])
            df['Lower Basic'] = (df['High'] + df['Low']) / 2 - (2 * df['ATR'])
            
            df['Supertrend'] = np.nan
            for i in range(1, len(df)):
                if df['Close'].iloc[i] > df['Upper Basic'].iloc[i-1]:
                    df['Supertrend'].iloc[i] = df['Lower Basic'].iloc[i]
                elif df['Close'].iloc[i] < df['Lower Basic'].iloc[i-1]:
                    df['Supertrend'].iloc[i] = df['Upper Basic'].iloc[i]
                else:
                    df['Supertrend'].iloc[i] = df['Supertrend'].iloc[i-1]

            df['Supertrend'] = df['Supertrend'].fillna(df['Lower Basic'])  # Fill NaN values in Supertrend
            
            return df.reset_index().to_dict('records')
        
        else:
            return {'error': 'Unexpected response format or error', 'details': data}

    except requests.RequestException as e:
        return {'error': 'Request failed', 'details': str(e)}

def scannerhome(request):
    api_key = settings.ALPHA_VANTAGE_API_KEY
    symbol = 'RELIANCE.BSE'

    data = get_daily_time_series(api_key, symbol)
    
    if isinstance(data, dict) and 'error' in data:
        context = data
    else:
        context = {
            'data': data
        }
    
    return render(request, "scannerhome.html", context)
