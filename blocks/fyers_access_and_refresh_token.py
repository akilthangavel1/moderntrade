# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
import creds

# Define your Fyers API credentials
client_id = creds.client_id  # Replace with your client ID
secret_key = creds.api_secret_key  # Replace with your secret key
redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"  # Replace with your redirect URI
response_type = "code" 
grant_type = "authorization_code"  

# The authorization code received from Fyers after the user grants access
auth_code = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkubG9naW4uZnllcnMuaW4iLCJpYXQiOjE3MjUwNjA0MjUsImV4cCI6MTcyNTA5MDQyNSwibmJmIjoxNzI1MDU5ODI1LCJhdWQiOiJbXCJ4OjBcIiwgXCJ4OjFcIiwgXCJ4OjJcIiwgXCJkOjFcIiwgXCJkOjJcIiwgXCJ4OjFcIiwgXCJ4OjBcIl0iLCJzdWIiOiJhdXRoX2NvZGUiLCJkaXNwbGF5X25hbWUiOiJZQTI5Mzk2Iiwib21zIjoiSzEiLCJoc21fa2V5IjoiYmVjYzQ0NTg2ZmM3YzI5MWExZmNhMDBmZWMyMDZiZDQyM2I5OGVkNGJhZjgyNzdiNmExYjljZTYiLCJub25jZSI6IiIsImFwcF9pZCI6Ik1NS1FUV05KSDMiLCJ1dWlkIjoiNmY5NDM1Y2EwYTFjNGU5M2IyYjYyNzVhODgzMTJlZTYiLCJpcEFkZHIiOiIwLjAuMC4wIiwic2NvcGUiOiIifQ.G8lWI7uC66-_FleTOoqLAD0ewHAjfo8u5pMQCxNCKCU"

# Create a session object to handle the Fyers API authentication and token generation
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key, 
    redirect_uri=redirect_uri, 
    response_type=response_type, 
    grant_type=grant_type
)

# Set the authorization code in the session object
session.set_token(auth_code)

# Generate the access token using the authorization code
response = session.generate_token()

# Print the response, which should contain the access token and other details
print(response)


