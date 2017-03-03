'小助手, 线上版'
import time
import sys
import logging

formatter = logging.Formatter(
    '%(asctime)s %(filename)s [line:%(lineno)d]\n[%(levelname)s]  %(message)s',
    '[%d/%b/%Y %H:%M:%S]'
    )
handle = logging.FileHandler('static/run.log')
handle.setLevel(logging.INFO)
handle.setFormatter(formatter)
logger = logging.getLogger('itchat')
logger.addHandler(handle)

WEEK = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
EXCEPTIONS = (
    AttributeError, IOError, NotImplementedError,
    TimeoutError, IndexError, ConnectionError,
    ValueError, TypeError, RuntimeError, ConnectionAbortedError,
    IndentationError, InterruptedError, KeyError, StopIteration,
    )
TIMEOUT = 2

def info(msg):
    '打印日志'
    #msg = '%s %s' % (time.ctime(), msg)
    logger.info(msg)
