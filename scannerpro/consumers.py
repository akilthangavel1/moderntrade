import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder
from asgiref.sync import sync_to_async
import asyncio

class StockDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        # Get the model dynamically from the app registry
        TickerBase = apps.get_model('scannerpro', 'TickerBase')
        
        # Continuously fetch data and send it to the WebSocket
        while True:
            # Use sync_to_async to handle the synchronous database query
            data = await sync_to_async(lambda: list(TickerBase.objects.all().values()))()
            
            # Send data as JSON through WebSocket
            await self.send(text_data=json.dumps(data, cls=DjangoJSONEncoder))
            await asyncio.sleep(1)  # Adjust frequency as needed

    async def disconnect(self, close_code):
        pass

