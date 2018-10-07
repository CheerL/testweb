import threading
import asyncio
from functools import partial, wraps
from helper.utils.parallel import kill_thread

class LoopThread(threading.Thread):
    def __init__(self, target, loop, name):
        self.loop = loop
        super().__init__(target=target, args=(loop,), name=name)

    def kill(self):
        if not self.loop.is_closed():
            self.loop.stop()
            self.loop._thread_id = None
            self.loop.close()
        kill_thread(thread=self)

def kill_callback(loop, thread):
    thread.kill()

def none_callback(loop, thread):
    pass

def get_loop_and_thread(thread_name=None, daemon=False):
    def start_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    loop = asyncio.new_event_loop()
    thread = LoopThread(target=start_loop, loop=loop, name=thread_name)
    thread.daemon = daemon
    thread.start()
    return loop, thread

def async_run(async_func, loop=None, thread=None, callback=kill_callback, *args, **kwargs):
    if loop is None or thread is None:
        loop, thread = get_loop_and_thread()
    future = asyncio.run_coroutine_threadsafe(async_func(*args, **kwargs), loop)
    future.add_done_callback(lambda _: callback(loop, thread))

def async_wrap(loop=None, thread=None, callback=kill_callback):
    def _async_wrap(async_func):
        @wraps(async_func)
        def __async_wrap(*args, **kwargs):
            async_run(async_func, loop=loop, thread=thread, callback=callback, *args, **kwargs)
        return __async_wrap
    return _async_wrap
