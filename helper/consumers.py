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
        # print(self.scope)

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
        print(text_data, self.scope)
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
        print(event)
        await self.send(json.dumps(event['message']))

# message.reply_channel    一个客户端通道的对象
# message.reply_channel.send(chunk)  用来唯一返回这个客户端

# 当连接上时，发回去一个connect字符串

# def get_channel(path):
#     channel_name = re.findall(r'channel=(.*)', path)[0] if 'chatroom' in path else path.strip('/')
#     # return urlencode({'': channel_name})[1:].replace('%', '')
#     return channel_name


# @channel_session
# def ws_connect(message):
#     message.reply_channel.send({"accept": True})
#     channel_name = get_channel(message['path'])
#     Group(channel_name).add(message.reply_channel)
#     if channel_name not in ['login', 'log']:
#         log_connect_report = 'log channel is successfully connected, client %s:%s' % (
#             message.content['client'][0], message.content['client'][1]
#         )
#         message.reply_channel.send({'text': json.dumps({"msg": log_connect_report})})


# @channel_session
# def ws_disconnect(message):
#     channel_name = get_channel(message['path'])
#     Group(channel_name, channel_layer=message.channel_layer).discard(
#         message.reply_channel)


# @channel_session
# def ws_receive(message):
#     channel_name = get_channel(message['path'])
#     text = message.content['text']
#     Group(channel_name).send({'text': json.dumps({"msg": text})})
