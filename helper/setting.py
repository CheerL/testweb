'小助手, 线上版'
import os
from requests.packages.urllib3.exceptions import HTTPError, PoolError, MaxRetryError

from web.settings import BASE_DIR


HOST = 'http://pi.cheerl.site:8000'
VOICE_HOST = 'https://w7.cheerl.site/clock/voice/'
# 常量
LOG_PATH = os.path.join(BASE_DIR, 'log')
MEDIA_PATH = 'media'
MEDIA_IMAGE_PATH = os.path.join(MEDIA_PATH, 'images')
MEDIA_VOICE_PATH = os.path.join(MEDIA_PATH, 'voices')
MEDIA_HEAD_PATH = os.path.join(MEDIA_IMAGE_PATH, 'head')

HELPER_PKL = os.path.join(MEDIA_PATH, 'helper.pkl')
QR_PIC = os.path.join(MEDIA_IMAGE_PATH, 'QR.png')
WX_PIC = os.path.join(MEDIA_IMAGE_PATH, 'WX.png')
HEAD_PIC = os.path.join(MEDIA_IMAGE_PATH, 'robot_head.png')

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


for path in [LOG_PATH, MEDIA_PATH, MEDIA_IMAGE_PATH, MEDIA_VOICE_PATH, MEDIA_HEAD_PATH]:
    if os.path.exists(path) and os.path.isfile(path):
        os.remove(path)
    if not os.path.exists(path):
        os.makedirs(path)
