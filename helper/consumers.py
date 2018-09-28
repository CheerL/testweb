import json

from channels.layers import get_channel_layer
from channels.generic.websocket import AsyncWebsocketConsumer


async def group_send(channel, msg_dict, msg_type='helper_message'):
    msg = {
        'type': msg_type,
        'message': msg_dict
    }
    await get_channel_layer().group_send(channel, msg)


class HelperConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.client_ip, self.client_port = self.scope['client']
        self.channel = self.scope['url_route']['kwargs']['channel']

        await self.accept()
        await self.channel_layer.group_add(
            self.channel,
            self.channel_name
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.channel,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data, msg_type='helper_message'):
        # Send message to room group
        try:
            text_data = json.loads(text_data)
        except:
            pass

        if isinstance(text_data, dict) and'type' in text_data.keys():
            msg_type = text_data['type']
            del text_data['type']

        await self.channel_layer.group_send(
            self.channel,
            {
                'type': msg_type,
                'message': text_data
            }
        )

    # Receive message from room group
    async def helper_message(self, event):
        # Send message to WebSocket
        await self.send(json.dumps(event['message']))
