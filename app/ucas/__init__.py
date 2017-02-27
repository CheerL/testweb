from logging import getLogger

logger = getLogger('itchat')
WEEK = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
EXCEPTIONS = (
    AttributeError, IOError, NotImplementedError,
    TimeoutError, IndexError, ConnectionError,
    ValueError, TypeError, RuntimeError, ConnectionAbortedError,
    IndentationError, InterruptedError, KeyError, StopIteration,
    )
TIMEOUT = 10