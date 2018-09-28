import json
import os
import re
from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import itchat
from asgiref.sync import async_to_sync
from helper.consumers import group_send
from helper.helper import HELPER
from helper.models import Message, Robot
from helper.setting import EXCEPTIONS, HEAD_PIC, PKL_PATH, QR_PIC, WX_PIC
from helper.utils import async_utils, parallel

MSG_INIT = '请点击登录按钮'
MSG_ERROR = '错误,请重新登录'
MSG_LOGIN = '小助手运行中'
MSG_SCAN = '请扫描二维码'
MSG_LOGOUT = '成功退出'
MSG_RELOAD = '重新启动'
MSG_REMIND = '小助手提醒中'
MSG_COMFIRM = '请在手机上确认登录'

ITEM_LIST = [
    {'text': '登录', 'id': 'login'},
    {'text': '聊天', 'id': 'chat'},
    {'text': '日志', 'id': 'log'},
    {'text': '设置', 'id': 'setting'},
]


def index(request):
    return render(request, 'helper_frontend/index.html')


def redirect_index(request):
    return HttpResponseRedirect('/helper/')


def post_allowed_only(func):
    @wraps(func)
    def inner_func(request, *args, **kwargs):
        try:
            if request.method == 'POST':
                return func(request, *args, **kwargs)
            else:
                raise NotImplementedError('访问错误')
        except EXCEPTIONS as error:
            return JsonResponse(dict(res=False, msg=str(error)))
    return inner_func

# 登陆 api


def login_init(request):
    if HELPER.IS_LOGIN:
        status = 2
        msg = '%s成功登录' % HELPER.robot.nick_name
        pic = HEAD_PIC
    else:
        status = 0
        msg = MSG_INIT
        pic = WX_PIC
    return JsonResponse(dict(status=status, msg=msg, pic=pic,))


@csrf_exempt
@post_allowed_only
@async_to_sync
async def login(request):
    '终于登录了'
    async def qr_func(uuid, status, qrcode):
        if qrcode:
            with open(QR_PIC, 'wb') as pic:
                pic.write(qrcode)

            await HELPER.logger.info('成功获取二维码')
            await group_send('login', dict(
                status=1,
                msg=MSG_SCAN,
                pic=QR_PIC
            ))
        else:
            await HELPER.logger.info('等待确认登录')
            await group_send('login', dict(
                status=1,
                msg=MSG_COMFIRM,
                pic=WX_PIC
            ))

    async def login_func():
        user = itchat.search_friends()
        itchat.get_head_img(userName=user['UserName'], picDir=HEAD_PIC)
        robot = Robot.objects.get_or_create(uin=user['Uin'])[0]
        robot.nick_name = user['NickName']
        robot.save()
        HELPER.robot = robot
        HELPER.robot.apply_settings(HELPER.settings)
        await HELPER.logger.info('%s成功登录' % robot.nick_name)
        HELPER.wxname_update()
        HELPER.remind()
        HELPER.IS_LOGIN = True
        if os.path.exists(QR_PIC):
            os.remove(QR_PIC)
        await group_send('login', dict(
            status=2,
            msg='%s成功登录' % HELPER.robot.nick_name,
            pic=HEAD_PIC
        ))

    async def exit_func():
        HELPER.logout()
        await HELPER.logger.info(MSG_LOGOUT)

    async def login_main():
        try:
            # loop, thread = async_utils.get_loop_and_thread()
            await HELPER.logger.info('尝试登陆')
            itchat.auto_login(
                True, PKL_PATH, False, QR_PIC,
                async_utils.async_wrap(qr_func),
                async_utils.async_wrap(login_func),
                async_utils.async_wrap(exit_func)
            )
            itchat.run(debug=True, blockThread=False)
        except EXCEPTIONS as error:
            print(error)
            await group_send('login', dict(
                status=1,
                msg=MSG_ERROR,
                pic=WX_PIC
            ))

    await login_main()
    return JsonResponse(dict(res=True, msg=''))


@async_to_sync
async def login_stop(request):
    try:
        if os.path.exists(PKL_PATH):
            os.remove(PKL_PATH)
        HELPER.logout()
    except EXCEPTIONS as error:
        await group_send('login', dict(
            status=1,
            msg=MSG_ERROR,
            pic=WX_PIC
        ))
        return JsonResponse(dict(res=False, msg=str(error)))
    else:
        await group_send('login', dict(
            status=0,
            msg=MSG_INIT,
            pic=WX_PIC
        ))
        return JsonResponse(dict(res=True))


@csrf_exempt
@post_allowed_only
@async_to_sync
async def logout(request):
    '退出登录'
    if HELPER.IS_LOGIN:
        HELPER.logout()
        if os.path.exists(PKL_PATH):
            os.remove(PKL_PATH)
        await HELPER.logger.info(MSG_LOGOUT)
        await group_send('login', dict(
            status=0,
            msg=MSG_INIT,
            pic=WX_PIC
        ))
    return JsonResponse(dict(res=True, msg=''))


# 日志 api
def get_log(request, start=0, count=1):
    log_list = HELPER.logger.log_read(count=int(count), start=int(start))
    return JsonResponse(dict(log_list=log_list))


def get_log_all(request):
    log_list = HELPER.logger.log_read(count=-1, start=0)
    return HttpResponse('<br>'.join(log_list))


@csrf_exempt
@post_allowed_only
@async_to_sync
async def send_log(request):
    await group_send('log', {"msg": request.POST['msg']})
    return JsonResponse(dict(res=True, msg=''))


# 聊天 api
def chat_user(request):
    def chat_user_head(user):
        HELPER.get_head_img(user['user_name'], user['path'], user['name'])

    def str_multi_replace(ori_str):
        '一次性替换多个字符对, 返回结果字符串'
        replace_str = re.subn(r'[\\\"\'/.*<>|:?]', '_', ori_str)
        return replace_str[0]

    user_list = []
    for user in itchat.get_friends():
        temp_dict = {
            'name': user['RemarkName'] if user['RemarkName'] else user['NickName'],
            'nick_name': str_multi_replace(user['NickName']),
            'user_name': user['UserName']
        }
        temp_dict['path'] = 'static/head/%s.png' % temp_dict['nick_name']
        del temp_dict['nick_name']
        user_list.append(temp_dict)

    req_list = [(chat_user_head, (user,)) for user in user_list]
    parallel.run_thread_pool(req_list, is_lock=False)

    return JsonResponse(dict(user_list=user_list, count=len(user_list)))


@csrf_exempt
@post_allowed_only
def chat_send(request):
    '主动发送消息'
    msg = request.POST['msg']
    user = request.POST['user']
    HELPER.send(msg, user)
    return JsonResponse(dict(res=True, msg=''))


@csrf_exempt
@post_allowed_only
def chat_history(request):
    '获取历史消息'
    def history(user):
        for message in Message.objects.filter(robot=HELPER.robot).filter(user=user):
            message.send_to_client()

    user = request.POST['user']
    parallel.run_thread_pool([(history, (user,))], is_lock=False)
    return JsonResponse(dict(res=True, msg=''))


# 设置api
def get_setting(request):
    item_list = vars(HELPER.settings).items()
    bool_list = [
        {
            'name': name,
            'val': val
        }
        for name, val in item_list if isinstance(val, bool)
    ]
    text_list = [
        {
            'name': name,
            'val': val
        }
        for name, val in item_list
        if not isinstance(val, bool) and name != 'LAST_UPDATE' and name != 'FLEXIBLE_DAY'
    ]
    select_list = [
        {
            'name': 'FLEXIBLE_DAY',
            'val': HELPER.settings.trans_flexible_day()
        }
    ]
    return JsonResponse({
        'bool_list': bool_list,
        'text_list': text_list,
        'select_list': select_list
    })


@csrf_exempt
@post_allowed_only
@async_to_sync
async def change_setting(request):
    if HELPER.IS_LOGIN:
        try:
            res = json.loads(request.body.decode())
            HELPER.settings.change_settings(res)
            HELPER.robot.save_settings(HELPER.settings)
            return JsonResponse({'res': True, 'msg': '修改成功'})
        except EXCEPTIONS as error:
            await HELPER.logger.info(error)
            return JsonResponse({'res': False, 'msg': '修改失败'})
