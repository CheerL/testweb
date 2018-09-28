'小助手, 线上版'
import os
from requests.packages.urllib3.exceptions import HTTPError, PoolError, MaxRetryError

# 常量
LOG_PATH = 'static/log/'
PKL_PATH = 'static/helper.pkl'
QR_PIC = 'static/images/QR.png'
WX_PIC = 'static/images/begin.png'
HEAD_PIC = 'static/images/head.png'

# HOST = []
BEG_WEEK = 51
END_WEEK = 20
TIMEOUT = 2

TL_KEY = '71f28bf79c820df10d39b4074345ef8c'  # 图灵机器人密钥

EXCEPTIONS = (
    AttributeError, IOError, NotImplementedError, PoolError,
    TimeoutError, IndexError, ConnectionError, OSError, HTTPError, MaxRetryError,
    ValueError, TypeError, RuntimeError, ConnectionAbortedError,
    IndentationError, InterruptedError, KeyError, StopIteration,
)
COURSE_DICT = [
    [8, 30], [9, 20], [10, 30], [11, 20],
    [13, 30], [14, 20], [15, 30], [16, 20],
    [19, 00], [19, 50], [20, 50], [21, 30]
]
