'小助手, 线上版'
import time
import json
import logging
import requests
from channels import Group

#需要交叉引用的函数的提前声明
def error_report(error, user=None, up_rep=True):
    '错误处理, 向用户发送错误信息或继续上报错误'
    info(error)
    if up_rep:
        raise NotImplementedError(error)
    else:
        Helper.send(str(error), user)

def info(msg, is_report=False):
    '向文件输出日志, 并发送到log频道'
    url = 'http://0.0.0.0:8000/helper/log/send/'
    logger.info(msg)
    Group('log').send({'text': json.dumps({"log":log_read(log_path)[0]})})
    requests.post(url=url, data={'msg':log_read(log_path)[0]})
    if is_report:
        raise NotImplementedError(msg)

#需要交叉引用的变量的提前声明
HELPER = None

#交叉引用声明结束

#常量
log_path = 'static/run.log'
pkl_path = 'static/helper.pkl'
QR_pic = 'static/QR.png'
WX_pic = 'static/begin.png'

END_WEEK = 20
TIMEOUT = 2

TL_KEY = '71f28bf79c820df10d39b4074345ef8c' #图灵机器人密钥

EXCEPTIONS = (
    AttributeError, IOError, NotImplementedError,
    TimeoutError, IndexError, ConnectionError,
    ValueError, TypeError, RuntimeError, ConnectionAbortedError,
    IndentationError, InterruptedError, KeyError, StopIteration,
    )
COURSE_DICT = [
    [8, 30], [9, 20], [10, 30], [11, 20],
    [13, 30], [14, 20], [15, 30], [16, 20],
    [19, 00], [19, 50], [20, 50], [21, 30]
    ]

clients = []

#内部调用函数
def __get_logger():
    formatter = logging.Formatter(
        '[%(asctime)s] "%(levelname)s"  %(message)s',
        '%d/%b/%Y %H:%M:%S'
        )
    handle = logging.FileHandler(log_path)
    handle.setLevel(logging.INFO)
    handle.setFormatter(formatter)
    __logger = logging.getLogger('itchat')
    __logger.addHandler(handle)
    return __logger

#外部调用函数
def log_read(path=log_path, count=1, start=0):
    '从倒数start行读取count行日志, 返回一个列表'
    with open(path, 'r') as file:
        content = file.readlines()
        if count is -1 and start is 0:
            line_list = content[::-1]
        else:
            line_list = content[-1-start:-1-start-count:-1]
    return line_list

def get_now_week():
    '返回当前周次'
    BEG = 51
    NOW = time.localtime().tm_yday
    return (NOW - BEG) // 7

#内部函数定义量
logger = __get_logger()

#交叉引用
from .helper import Helper
from .models import Course, Coursetime, Helper_user

#交叉引用的变量的重定义
HELPER = Helper()
