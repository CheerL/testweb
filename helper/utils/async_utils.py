import threading
import asyncio
from functools import partial, wraps

def kill_callback(loop, thread):
    if not loop.is_closed():
        loop.stop()
        loop.close()
    if not thread._is_stopped:
        thread._stop()
        thread._delete()
    # print('kill thread & loop')

async def target_wrap(coro, loop, thread, callback):
    await coro
    if hasattr(callback, '__call__'):
        callback(loop, thread)

def get_loop_and_thread():
    def start_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    loop = asyncio.new_event_loop()
    loop_thread = threading.Thread(target=start_loop, args=(loop,), name='async_thread')
    loop_thread.daemon = True
    loop_thread.start()
    return loop, loop_thread

def async_run(async_func, loop=None, thread=None, callback=None, *args, **kwargs):
    if loop is None or thread is None:
        loop, thread = get_loop_and_thread()
        callback = kill_callback
    asyncio.run_coroutine_threadsafe(target_wrap(async_func(*args, **kwargs), loop, thread, callback), loop)

def async_wrap(loop=None, thread=None, callback=None):
    def _async_wrap(async_func):
        @wraps(async_func)
        def __async_wrap(*args, **kwargs):
            async_run(async_func, loop=loop, thread=thread, callback=callback, *args, **kwargs)
        return __async_wrap
    return _async_wrap
