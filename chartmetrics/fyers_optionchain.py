from fyers_apiv3 import fyersModel
from scannerpro.views import get_access_token

client_id = "MMKQTWNJH3-100"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE3MzM3MjAyNTMsImV4cCI6MTczMzc5MDYzMywibmJmIjoxNzMzNzIwMjUzLCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCblZuaTlnM0NQTFNVenVPeWlrU3U5Nkc2RGpULUVIYjJDTU4yMzl1elVtUS1IaXh4eVUwZ0hTaDV5cHAzWnZuVy1YMnNUc0h2aEVsRjNVQ0pOYkp4bF9TS01qVXRaV0RldDBZajVqVlBBa2tQcncxWT0iLCJkaXNwbGF5X25hbWUiOiJBS0lMIFRIQU5HQVZFTCIsIm9tcyI6IksxIiwiaHNtX2tleSI6ImJlY2M0NDU4NmZjN2MyOTFhMWZjYTAwZmVjMjA2YmQ0MjNiOThlZDRiYWY4Mjc3YjZhMWI5Y2U2IiwiZnlfaWQiOiJZQTI5Mzk2IiwiYXBwVHlwZSI6MTAwLCJwb2FfZmxhZyI6Ik4ifQ.-1jcrmEYK1PxSKLh7dRzxy4wS46zeIc0vbt6fUbtamI"


def get_option_chain_data(symbol):
    fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=False, log_path="")
    data = {
        "symbol":symbol,
        "strikecount":25,
        "timestamp": ""
    }
    response = fyers.optionchain(data=data);
    return response


def get_option_quotes(symbol_quotes):
    fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=False, log_path="")

    data = {
        "symbols":symbol_quotes
    }

    response = fyers.quotes(data=data)
    return response
