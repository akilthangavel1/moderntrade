from fyers_apiv3 import fyersModel
import creds

client_id = creds.client_id
access_token = creds.access_token
# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=False, log_path="")
data = {
    "symbol":"NSE:TCS-EQ",
    "strikecount":1,
    "timestamp": ""
}
response = fyers.optionchain(data=data);
print(response)
