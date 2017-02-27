'手动改写登陆函数'
import io
import os
import time
import sys
import itchat
import requests
from pyqrcode import QRCode
from itchat.utils import test_connect
from . import logger, EXCEPTIONS, TIMEOUT

def login(pic_dir):
    '来吧复杂的登陆函数'
    #如果无法链接, 就退出
    try:
        url = 'https://login.weixin.qq.com/'
        requests.get(url, timeout=TIMEOUT)
        uuid = __open_qr(pic_dir)
        yield '/' + pic_dir
        __login_after_qr(uuid, pic_dir)
        os.remove(pic_dir)
        yield
    except EXCEPTIONS as error:
        logger.info(error)
        raise NotImplementedError('登陆出错, 请重新登陆')

def __open_qr(pic_dir):
    for _ in range(3):
        logger.info('Getting uuid')
        uuid = itchat.get_QRuuid()
        #收到uuid为止
        while uuid is None:
            uuid = itchat.get_QRuuid()
            time.sleep(1)
        logger.info('Getting QR Code')
        #如果成功获取二维码, 跳出循环
        time.sleep(1)
        if __get_qr(uuid, pic_dir):
            break
    #否则重试3次
    else:
        logger.info('Failed to get QR Code, please restart the program')
        sys.exit()
    logger.info('Please scan the QR Code')
    return uuid

def __login_after_qr(uuid, pic_dir):
    wait_confirm = True
    while True:
        time.sleep(1)
        logger.info('检查扫码状态')
        status = itchat.check_login(uuid)
        if status == '200':
            break
        elif status == '201':
            if wait_confirm:
                logger.info('请扫码')
                wait_confirm = False
        elif status == '408':
            logger.info('请重新登陆')
            raise NotImplementedError('二维码失效')
    userInfo = itchat.web_init()
    itchat.show_mobile_login()
    itchat.get_contact(True)

    msg = '%s 成功登录' % userInfo['User']['NickName']
    logger.info(msg)
    itchat.start_receiving()

def __get_qr(uuid, pic_dir):
    qrStorage = io.BytesIO()
    qrCode = QRCode('https://login.weixin.qq.com/l/' + uuid)
    time.sleep(1)
    qrCode.png(qrStorage, scale=10)
    with open(pic_dir, 'wb') as f:
        f.write(qrStorage.getvalue())
    return qrStorage
