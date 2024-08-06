import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_intraday_data(symbol, interval='5m'):
    # Define end time as now
    end_time = datetime.now()
    # Define start time as the beginning of yesterday
    start_time = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    try:
        # Download data
        df = yf.download(symbol, start=start_time, end=end_time, interval=interval)
        
        if not df.empty:
            # Print DataFrame columns for debugging
            print("DataFrame Columns:", df.columns)
            
            # Reset index to get 'Datetime' column
            df.reset_index(inplace=True)
            
            # Rename columns based on actual DataFrame structure
            df.columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume'] + list(df.columns[6:])
            
            # Convert 'Datetime' to string in 'YYYY-MM-DD HH:MM:SS' format
            df['Datetime'] = df['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Return the data as a list of dictionaries
            return df.to_dict('records')
        
        else:
            return {'error': 'No data available for the given parameters'}
    
    except Exception as e:
        return {'error': 'Failed to fetch data', 'details': str(e)}

# Example usage
symbol = 'AAPL'
data = get_intraday_data(symbol)
print(data)
