from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/stock-data/', consumers.StockDataConsumer.as_asgi()),
]
