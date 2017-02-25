'手动改写登陆函数'
import time
import sys
import logging
import itchat
from itchat.utils import test_connect

logger = logging.getLogger('itchat')
PKL = 'static/itchat.pkl'

def login(pic_dir, hot_reload=True):
    if not test_connect():
        logger.info("You can't get access to internet or wechat domain, so exit.")
        sys.exit()
    if hotReload:
        if itchat.load_login_status(PKL):
            return
        __login(pic_dir)
        itchat.dump_login_status(PKL)
        hotReloadDir = PKL
    else:
        __login(pic_dir)

def __open_QR(pic_dir):
    
    return uuid

def __login(pic_dir):
    for get_count in range(10):
        logger.info('Getting uuid')
        uuid = itchat.get_QRuuid()
        while uuid is None:
            uuid = itchat.get_QRuuid()
            time.sleep(1)
        logger.info('Getting QR Code')
        if itchat.get_QR(uuid, picDir=pic_dir): break
        elif get_count >= 9:
            logger.info('Failed to get QR Code, please restart the program')
            sys.exit()
    logger.info('Please scan the QR Code')
    waitForConfirm = False
    while True:
        status = itchat.check_login(uuid)
        if status == '200':
            break
        elif status == '201':
            if waitForConfirm:
                logger.info('Please press confirm')
                waitForConfirm = True
        elif status == '408':
            logger.info('Reloading QR Code')
            uuid = __open_QR(pic_dir)
            waitForConfirm = False
    userInfo = itchat.web_init()
    itchat.show_mobile_login()
    itchat.get_contact(True)
    msg = 'Login successfully as %s' % userInfo['User']['NickName']
    logger.info(msg)
    itchat.start_receiving()

# Start auto-replying
@itchat.msg_register
def simple_reply(msg):
    if msg['Type'] == 'Text':
        return 'I received: %s' % msg['Content']

itchat.run()