'小助手, 线上版'
import time
import sys
import logging
from .. import views

log_path = 'static/run.log'
pkl_path = 'static/helper.pkl'
QR_pic = 'static/QR.png'
WX_pic = 'static/begin.png'

formatter = logging.Formatter(
    '[%(asctime)s] "%(levelname)s"  %(message)s',
    '%d/%b/%Y %H:%M:%S'
    )
handle = logging.FileHandler(log_path)
handle.setLevel(logging.INFO)
handle.setFormatter(formatter)
logger = logging.getLogger('itchat')
logger.addHandler(handle)

END_WEEK = 20
WEEK = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
WEEK_DICT = dict(map(lambda x, y: [x, y], WEEK, [i for i in range(7)]))
COURSE_NUM = [str(i) for i in range(1, 12)]
COURSE_DICT = dict(map(lambda x, y: [x, y], COURSE_NUM, (
    [8, 30], [9, 20], [10, 30], [11, 20],
    [13, 30], [14, 20], [15, 30], [16, 20],
    [19, 00], [19, 50], [20, 50]
    )))


EXCEPTIONS = (
    AttributeError, IOError, NotImplementedError,
    TimeoutError, IndexError, ConnectionError,
    ValueError, TypeError, RuntimeError, ConnectionAbortedError,
    IndentationError, InterruptedError, KeyError, StopIteration,
    )
TIMEOUT = 2

def log_read(path=log_path, count=1, start=0):
    with open(path, 'r') as file:
        content = file.readlines()
        if count is -1 and start is 0:
            line_list = content[::-1]
        else:
            line_list = content[-1-start:-1-start-count:-1]
    return line_list

def info(msg):
    '打印日志'
    logger.info(msg)
    views.send(log_read(log_path)[0])
