import json
import time
from channels import Group
from channels.sessions import channel_session

# message.reply_channel    一个客户端通道的对象
# message.reply_channel.send(chunk)  用来唯一返回这个客户端

# 一个管道大概会持续30s

# 当连接上时，发回去一个connect字符串


@channel_session
def ws_connect(message):
    # message.reply_channel.send({"connect"})
    message.reply_channel.send({"accept": True})
    # message.reply_channel.send({'text':json.dumps({"msg":'1'})})
    path = message['path'].strip('/')
    if path == 'log':
        Group(path).add(message.reply_channel)
        log_connect_report = 'log channel is successfully connected, client %s:%s' % (
            message.content['client'][0], message.content['client'][1]
        )
        message.reply_channel.send(
            {'text': json.dumps({"msg": log_connect_report})})
    if path == 'login':
        Group(path).add(message.reply_channel)
    # message.reply_channel.send({'text':json.dumps({"msg":'2'})})
    # message.reply_channel.send({'text':json.dumps({"msg":'3'})})
    # except ValueError:
    #     log.debug('invalid ws path=%s', message['path'])
    #     return
    # except Room.DoesNotExist:
    #     log.debug('ws room does not exist label=%s', label)
    #     return

    # log.debug('chat connect room=%s client=%s:%s',
    #     room.label, message['client'][0], message['client'][1])
    # Need to be explicit about the channel layer so that testability works
    # This may be a FIXME?
    # message.channel_session['log'] = room.label

# 将发来的信息原样返回


@channel_session
def ws_disconnect(message):
    # message.reply_channel.send({"disconnect"})
    path = message['path'].strip('/')
    # if path == 'log':
    if True:
        Group(path, channel_layer=message.channel_layer).discard(
            message.reply_channel)


@channel_session
def ws_receive(message):
    path = message['path'].strip('/')
    text = message.content['text']
    # if path == 'log':
    if True:
        Group(path).send({'text': json.dumps({"msg": text})})
