'手动改写登陆函数'
import io
import os
import time
import sys
import itchat
import requests
from pyqrcode import QRCode
from . import info, EXCEPTIONS, TIMEOUT, pkl_dir
from .main import HELPER

def login(pic_dir, status, uuid=None):
    '来吧登陆函数'
    #如果无法链接, 就退出
    try:
        if os.path.isfile(pkl_dir) and itchat.load_login_status(pkl_dir):
            info('HotReload成功')
            itchat.run(blockThread=False)
            HELPER.is_login = True
            return 'hot', None
        if status == 0:
            url = 'https://login.weixin.qq.com/'
            requests.get(url, timeout=TIMEOUT)
            uuid = __get_qr(pic_dir)
            return 'uuid', uuid
        elif status == 1:
            __login_after_qr(uuid)
            os.remove(pic_dir)
            return True
        else:
            return False
    except EXCEPTIONS as error:
        info(error)
        raise

def __get_qr(pic_dir):
    for _ in range(3):
        info('正在获取uuid')
        uuid = itchat.get_QRuuid()
        #收到uuid为止
        while uuid is None:
            uuid = itchat.get_QRuuid()
            time.sleep(1)
        info('正在获取二维码')
        #如果成功获取二维码, 跳出循环
        time.sleep(1)
        if __is_qr(uuid, pic_dir):
            break
    #否则重试3次
    else:
        info('获取二维码失败, 请重启程序')
        sys.exit()
    info('成功获取二维码')
    return uuid

def __is_qr(uuid, pic_dir):
    qrStorage = io.BytesIO()
    qrCode = QRCode('https://login.weixin.qq.com/l/' + uuid)
    time.sleep(1)
    qrCode.png(qrStorage, scale=10)
    with open(pic_dir, 'wb') as file:
        file.write(qrStorage.getvalue())
    return True

def __login_after_qr(uuid):
    while True:
        time.sleep(1)
        info('检查扫码状态')
        status = itchat.check_login(uuid)
        if status == '200':
            info('已确认登陆')
            break
        elif status == '408':
            info('请重新登陆')
            raise NotImplementedError('二维码失效')
    userInfo = itchat.web_init()
    itchat.show_mobile_login()
    itchat.get_contact(True)
    info('%s 成功登录' % userInfo['User']['NickName'])
    itchat.start_receiving()
    itchat.run(blockThread=False)
    itchat.dump_login_status(pkl_dir)
    HELPER.is_login = True
