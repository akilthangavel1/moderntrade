from fyers_apiv3 import fyersModel
import time
from datetime import datetime
import pandas as pd
import numpy as np

client_id = "MMKQTWNJH3-100"
secret_key = "EUT312TGNM"
redirect_url = "http://localhost:4004/"

def date_to_timestamp(date_str, date_format="%d/%m/%Y"):
    dt = datetime.strptime(date_str, date_format)
    return int(time.mktime(dt.timetuple()))


def atr(DF, n):
    df = DF.copy()
    df['H-L'] = abs(df['high'] - df['low'])
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].ewm(com=n, min_periods=n).mean()
    return df['ATR']


def supertrend(DF, n, m):
    df = DF.copy()
    df['ATR'] = atr(df, n)
    df["B-U"] = ((df['high'] + df['low']) / 2) + m * df['ATR']
    df["B-L"] = ((df['high'] + df['low']) / 2) - m * df['ATR']
    df["U-B"] = df["B-U"]
    df["L-B"] = df["B-L"]
    ind = df.index
    for i in range(n, len(df)):
        if df['close'][i-1] <= df['U-B'][i-1]:
            df.loc[ind[i], 'U-B'] = min(df['B-U'][i], df['U-B'][i-1])
        else:
            df.loc[ind[i], 'U-B'] = df['B-U'][i]    
    for i in range(n, len(df)):
        if df['close'][i-1] >= df['L-B'][i-1]:
            df.loc[ind[i], 'L-B'] = max(df['B-L'][i], df['L-B'][i-1])
        else:
            df.loc[ind[i], 'L-B'] = df['B-L'][i]  
    df['Strend'] = np.nan
    for test in range(n, len(df)):
        if df['close'][test-1] <= df['U-B'][test-1] and df['close'][test] > df['U-B'][test]:
            df.loc[ind[test], 'Strend'] = df['L-B'][test]
            break
        if df['close'][test-1] >= df['L-B'][test-1] and df['close'][test] < df['L-B'][test]:
            df.loc[ind[test], 'Strend'] = df['U-B'][test]
            break
    for i in range(test+1, len(df)):
        if df['Strend'][i-1] == df['U-B'][i-1] and df['close'][i] <= df['U-B'][i]:
            df.loc[ind[i], 'Strend'] = df['U-B'][i]
        elif df['Strend'][i-1] == df['U-B'][i-1] and df['close'][i] >= df['U-B'][i]:
            df.loc[ind[i], 'Strend'] = df['L-B'][i]
        elif df['Strend'][i-1] == df['L-B'][i-1] and df['close'][i] >= df['L-B'][i]:
            df.loc[ind[i], 'Strend'] = df['L-B'][i]
        elif df['Strend'][i-1] == df['L-B'][i-1] and df['close'][i] <= df['L-B'][i]:
            df.loc[ind[i], 'Strend'] = df['U-B'][i]
    return df['Strend']


def fetch_ohlc_data(symbol, resolution, from_date, to_date, client_id, access_token, date_format="%d/%m/%Y"):
    fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")
    range_from = date_to_timestamp(from_date, date_format)
    range_to = date_to_timestamp(to_date, date_format) + 24 * 60 * 60
    data = {
        "symbol": symbol,
        "resolution": resolution,        
        "date_format": "0",              
        "range_from": str(range_from),   
        "range_to": str(range_to),       
        "cont_flag": "1"                
    }
    
    try:
        response = fyers.history(data=data)
        if response.get('s') == 'ok':
            return response
        else:
            return f"Error in response: {response}"
    except Exception as e:
        return f"An error occurred: {e}"
    

def process_ohlc_data(response):
    if 'candles' not in response:
        return "No candle data found in response."
    candles = response['candles']
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
    return df


def get_stock_list():
    df1 = pd.read_csv('ind_nifty500list.csv')
    stock_lis = []
    for value in df1['Symbol']:
        stock_lis.append("NSE:" + value + "-EQ")
    return stock_lis


import time
import pandas as pd
from datetime import datetime
import traceback

def run_supertrend_analysis():
    ticker_list = get_stock_list()
    resolution = "D"
    from_date = "13/01/2024"
    to_date = "28/09/2024"

    # Create a Pandas DataFrame to store the signals
    signals_data = pd.DataFrame(columns=['Datetime', 'Ticker', 'Signal'])

    for ticker in ticker_list:
        try:
            raw_ohlc_data = fetch_ohlc_data(ticker, resolution, from_date, to_date, client_id, access_token)
            ohlc_data = process_ohlc_data(raw_ohlc_data)
            print(ohlc_data)
            time.sleep(1)

            if isinstance(ohlc_data, pd.DataFrame):
                supertrend_data = supertrend(ohlc_data, 10, 1)
                ohlc_data['Supertrend'] = supertrend_data
                ohlc_data['volume'] = pd.to_numeric(ohlc_data['volume'])

                last_volume = ohlc_data['volume'].iloc[-1]
                previous_volume = ohlc_data['volume'].iloc[-2]
                last_supertrend = ohlc_data['Supertrend'].iloc[-1]
                previous_supertrend = ohlc_data['Supertrend'].iloc[-2]
                last_close = ohlc_data['close'].iloc[-1]
                previous_close = ohlc_data['close'].iloc[-2]

                if last_volume > previous_volume:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    if last_supertrend < last_close and previous_supertrend > previous_close:
                        print(current_time, ticker, 'Supertrend BUY')
                        # You can append to signals_data if needed
                    elif last_supertrend > last_close and previous_supertrend < previous_close:
                        print(current_time, ticker, 'Supertrend SELL')
                        # You can append to signals_data if needed
                else:
                    pass
            else:
                print(f"Failed to process data for {ticker}: {ohlc_data}")

        except Exception as e:
            print(f"Error encountered for ticker {ticker}: {str(e)}")
            traceback.print_exc()  # Optional: Print the full traceback for debugging
            print("Sleeping for 5 minutes before retrying...")
            time.sleep(300)  # Sleep for 5 minutes (300 seconds)
            return  # Stop current run and restart after 5 minutes

if __name__ == "__main__":
    while True:
        run_supertrend_analysis()
