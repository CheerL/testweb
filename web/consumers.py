import re
import json
import time
from channels import Group
from channels.sessions import channel_session

# message.reply_channel    一个客户端通道的对象
# message.reply_channel.send(chunk)  用来唯一返回这个客户端

# 当连接上时，发回去一个connect字符串

def get_channel(path):
    return re.findall(r'channel=(.*)', path)[0] if 'chatroom' in path else path.strip('/')


@channel_session
def ws_connect(message):
    message.reply_channel.send({"accept": True})
    channel_name = get_channel(message['path'])
    Group(channel_name).add(message.reply_channel)
    if channel_name not in ['login', 'log']:
        log_connect_report = 'log channel is successfully connected, client %s:%s' % (
            message.content['client'][0], message.content['client'][1]
        )
        message.reply_channel.send({'text': json.dumps({"msg": log_connect_report})})


@channel_session
def ws_disconnect(message):
    channel_name = get_channel(message['path'])
    Group(channel_name, channel_layer=message.channel_layer).discard(
        message.reply_channel)


@channel_session
def ws_receive(message):
    channel_name = get_channel(message['path'])
    text = message.content['text']
    Group(channel_name).send({'text': json.dumps({"msg": text})})
