
import time
from functools import wraps
from django.http import JsonResponse

def post_allowed_only(func):
    @wraps(func)
    def _post_allowed_only(request, *args, **kwargs):
        try:
            if request.method == 'POST':
                return func(request, *args, **kwargs)
            else:
                raise NotImplementedError('访问错误')
        except Exception as error:
            return JsonResponse(dict(res=False, msg=str(error)))
    return _post_allowed_only

def time_limit(limit_sec):
    def _time_limit(func):
        last_use = [0]
        cache = [None]
        @wraps(func)
        def __time_limit(request, *args, **kwargs):
            now = time.time()
            if now - last_use[0] > limit_sec:
                cache[0] = func(request, *args, **kwargs)
            return cache[0]
        return __time_limit
    return _time_limit
