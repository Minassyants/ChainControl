import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotifConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(str(self.scope['user'].id),self.channel_name)
        await self.accept()
        #text_data = {'text':"HELLO SUKAS"}
        #await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(str(self.scope['user'].id),self.channel_name)

    async def send_notif(self,event):
        
        await self.send(text_data=event['text'])