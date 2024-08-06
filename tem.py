import requests

api_key = '4UDTH4C8D430REJJ'
symbol = 'RELIANCE.BSE'
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'

response = requests.get(url)
data = response.json()
print(data)