from fyers_apiv3 import fyersModel
import creds

client_id = creds.client_id
access_token = creds.access_token

# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

data = {
    "symbol":"NSE:WIPRO-EQ",
    "resolution":"D",
    "date_format":"0",
    "range_from":"1690895316",
    "range_to":"1691068173",
    "cont_flag":"1"
}

response = fyers.history(data=data)
print(response)

