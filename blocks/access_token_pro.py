import creds
from fyers_apiv3 import fyersModel


client_id = creds.client_id
secret_key =  creds.api_secret_key
redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
response_type = "code" 
state = "sample_state"



session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type=response_type
)


response = session.generate_authcode()


print(response)



client_id = creds.client_id  
secret_key = creds.api_secret_key 
redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"  
response_type = "code" 
grant_type = "authorization_code"  


auth_code = input("Enter the auth code")


session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key, 
    redirect_uri=redirect_uri, 
    response_type=response_type, 
    grant_type=grant_type
)


session.set_token(auth_code)


response = session.generate_token()


print(" ")
print(response['access_token'])



