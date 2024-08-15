from fyers_apiv3 import fyersModel
import creds

client_id = creds.client_id
access_token = creds.access_token

# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=True, log_path="")

# Make a request to get the funds information
# response = fyers.funds()
# print(response)
import asyncio

async def get_funds():
    response = await fyers.funds()
    print(response)

asyncio.run(get_funds())
