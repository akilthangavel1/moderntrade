from fyers_apiv3 import fyersModel
import creds
import time
from datetime import datetime

# Function to convert date to Unix timestamp
def date_to_timestamp(date_str, date_format="%d/%m/%Y"):
    dt = datetime.strptime(date_str, date_format)
    return int(time.mktime(dt.timetuple()))

# Initialize credentials
client_id = creds.client_id
access_token = creds.access_token

# Initialize the FyersModel instance
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

# Dates for the request
from_date = "13/08/2024"
to_date = "15/08/2024"

# Convert dates to Unix timestamps
range_from = date_to_timestamp(from_date)
range_to = date_to_timestamp(to_date) + 24 * 60 * 60  # Adding one day to include the end date

# Data dictionary for API request
data = {
    "symbol": "NSE:SBIN-EQ",        # Symbol for the stock
    "resolution": "1",              # Time resolution (1 minute)
    "date_format": "0",             # Date format (0 for YYYY-MM-DD)
    "range_from": str(range_from),  # Start timestamp
    "range_to": str(range_to),      # End timestamp
    "cont_flag": "1"                # Continuous flag (1 for continuous data)
}

try:
    # Fetch historical data from the Fyers API
    response = fyers.history(data=data)
    
    # Check if response is successful
    if response.get('s') == 'ok':
        print(response)
    else:
        print("Error in response:", response)
except Exception as e:
    print("An error occurred:", e)
