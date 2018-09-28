import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.client_ip, self.client_port = self.scope['client']
        self.channel = self.scope['url_route']['kwargs']['channel']

        self.accept()
        self.send(json.dumps({
            'channel': 'system',
            'msg': 'client %s:%d successfully connect to channel %s' % (
                self.client_ip, self.client_port, self.channel
            )
        }))
        async_to_sync(self.channel_layer.group_add)(
            self.channel,
            self.channel_name
        )

    def disconnect(self, close_code):
        # Leave room group
        self.send(json.dumps({
            'channel': 'system',
            'msg':  'client %s:%d successfully disconnect to channel %s' % (
                self.client_ip, self.client_port, self.channel
            )
        }))
        async_to_sync(self.channel_layer.group_discard)(
            self.channel,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.channel,
            {
                'type': 'chat_message',
                'message': {
                    'channel': self.channel,
                    'msg': text_data
                }
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        # Send message to WebSocket
        self.send(json.dumps(event['message']))
