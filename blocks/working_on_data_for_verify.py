from fyers_apiv3 import fyersModel
import creds
import pandas as pd

client_id = creds.client_id
access_token = creds.access_token

fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")
data = {
    "symbol": "NSE:SBIN-EQ",
    "strikecount": 10,
    "timestamp": ""
}

response = fyers.optionchain(data=data)
# print(response)
# Open the file in write mode
with open("option_chain_output.txt", "w") as file:

    if 'data' in response:
        if 'expiryData' in response['data']:
            for expiry in response['data']['expiryData']:
                file.write(f"Expiry: {expiry}\n")
        
        if 'optionsChain' in response['data']:
            count = 0
            for option in response['data']['optionsChain']:
                if count == 0:
                    count += 1
                else:
                    file.write(f"ASK: {option['ask']}\n")
                    file.write(f"BID: {option['bid']}\n")
                    file.write(f"LTP: {option['ltp']}\n")
                    file.write(f"Strike Price: {option['strike_price']}\n")
                    file.write(f"OI: {option['oi']}\n")
                    file.write(f"Volume: {option['volume']}\n")
                    file.write(f"Symbol: {option['symbol']}\n")
                    file.write(f"Option Type: {option['option_type']}\n")
                    file.write("*" * 20 + "\n")
                    
    else:
        file.write("Error in response, data not found.\n")

print("Output written to option_chain_output.txt")
