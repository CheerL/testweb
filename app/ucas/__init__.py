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

pic_dir = 'static/QR.png'
pkl_dir = 'static/helper.pkl'

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

def try_more_times(error_func=None, times=5, sleep_time=0, re_run=False):
    '多次运行函数, 默认次数5次, 不休眠, 不重复'
    def _try(func):
        def __try(*arg, **kwargs):
            run_count = 1
            while True:
                try:
                    func(*arg, **kwargs)
                    if not re_run or run_count >= times:
                        break
                except EXCEPTIONS as error:
                    info(error)
                    if run_count >= times:
                        if error_func:
                            error_func()
                        break
                run_count += 1
                time.sleep(sleep_time)
                info('开始第%d次尝试' % run_count)
        return __try
    return _try
