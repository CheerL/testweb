from channels import Group
from channels.sessions import channel_session

#message.reply_channel    一个客户端通道的对象
#message.reply_channel.send(chunk)  用来唯一返回这个客户端

#一个管道大概会持续30s

#当连接上时，发回去一个connect字符串
@channel_session
def ws_connect(message):
    # message.reply_channel.send({"connect"})
    pass

#将发来的信息原样返回
@channel_session
def ws_message(message):
    # message.reply_channel.send({
    #     "text": message.content['text'],
    # })
    pass
#断开连接时发送一个disconnect字符串，当然，他已经收不到了
@channel_session
def ws_disconnect(message):
    # message.reply_channel.send({"disconnect"})
    pass

@channel_session
def ws_receive(message):
    pass
