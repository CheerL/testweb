import time
import hmac
import hashlib
from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.


def index(request):
    return render(request, 'ssh/ssh.html')


def get_auth_obj(request):
    # 安装gateone的服务器以及端口.
    gateone_server = 'http://localhost:443'
    secret = b"OTFjZTFlZDhhYjgzNDRkY2I1NTdmY2U0MTA1MmU1YzFkO"
    api_key = "YWI2MjM3ZDk5YmYxNDlhOWJlZjdiNTY4MmRlMzU4YzI2M"

    authobj = {
        'api_key': api_key,
        'upn': "gateone",
        'timestamp': str(int(time.time() * 1000)),
        'signature_method': 'HMAC-SHA1',
        'api_version': '1.0'
    }
    my_hash = hmac.new(secret, digestmod=hashlib.sha1)
    my_hash_update = authobj['api_key'] + authobj['upn'] + authobj['timestamp']
    my_hash.update(my_hash_update.encode())

    authobj['signature'] = my_hash.hexdigest()
    auth_info_and_server = {"url": gateone_server, "auth": authobj}
    return JsonResponse(auth_info_and_server)
