import json
import time
import os
import re

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import itchat
from asgiref.sync import async_to_sync
from helper.consumers import group_send
from helper.helper import HELPER
from helper.models import Message, Robot, Setting
from helper.setting import EXCEPTIONS, HEAD_PIC, HELPER_PKL, QR_PIC, WX_PIC, MEDIA_HEAD_PATH
from helper.utils import async_utils, parallel, post_allowed_only, time_limit
import helper.reply


MSG_INIT = '请点击登录按钮'
MSG_ERROR = '错误, 请重新登录'
MSG_LOGIN = '小助手运行中'
MSG_SCAN = '请扫描二维码'
MSG_LOGOUT = '成功退出'
MSG_RELOAD = '重新启动'
MSG_REMIND = '小助手提醒中'
MSG_COMFIRM = '请在手机上确认登录'
MSG_COMFIRMED = '确认登录, 请稍候'

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
def login(request):
    '终于登录了'
    @time_limit(1)
    @async_utils.async_wrap()
    async def qr_func(uuid, status, qrcode):
        if qrcode and status in ['408', '0']:
            with open(QR_PIC, 'wb') as pic:
                pic.write(qrcode)

            await HELPER.logger.info('成功获取二维码')
            await group_send('login', dict(
                status=1,
                msg=MSG_SCAN,
                pic=QR_PIC
            ))
        elif status == '201':
            await HELPER.logger.info('等待确认登录')
            await group_send('login', dict(
                status=1,
                msg=MSG_COMFIRM,
                pic=WX_PIC
            ))
        elif status == '200':
            await HELPER.logger.info('登录成功请稍候')
            await group_send('login', dict(
                status=1,
                msg=MSG_COMFIRMED,
                pic=WX_PIC
            ))

    @async_utils.async_wrap()
    async def login_func():
        user = itchat.search_friends()
        itchat.get_head_img(userName=user['UserName'], picDir=HEAD_PIC)
        robot = Robot.objects.get_or_create(uin=user['Uin'])[0]
        robot.nick_name = user['NickName']
        if robot.settings == 'None':
            robot.settings = Setting.objects.create()
        robot.save()
        HELPER.IS_LOGIN = True
        HELPER.robot = robot
        if os.path.exists(QR_PIC):
            os.remove(QR_PIC)
        await HELPER.logger.info('%s成功登录' % robot.nick_name)
        await group_send('login', dict(
            status=2,
            msg='%s成功登录' % HELPER.robot.nick_name,
            pic=HEAD_PIC
        ))

    @async_utils.async_wrap()
    async def exit_func():
        try:
            parallel.search_thread(name='login', part=True).kill()
        except:
            pass
        HELPER.logout()
        await HELPER.logger.info(MSG_LOGOUT)
        await group_send('login', dict(
            status=1,
            msg=MSG_ERROR,
            pic=WX_PIC
        ))

    async def login_main():
        try:
            await HELPER.logger.info('尝试登陆')
            itchat.auto_login(
                True, HELPER_PKL, False, QR_PIC,
                qr_func, login_func, exit_func
            )
            itchat.run(debug=False, blockThread=False)
        except EXCEPTIONS as error:
            print(error)
            await group_send('login', dict(
                status=1,
                msg=MSG_ERROR,
                pic=WX_PIC
            ))

    loop, thread = async_utils.get_loop_and_thread('login')
    async_utils.async_run(login_main, loop, thread)
    return JsonResponse(dict(res=True, msg=''))


@async_to_sync
async def login_stop(request):
    try:
        try:
            parallel.search_thread(name='login', part=True).kill()
        except:
            pass
        if os.path.exists(HELPER_PKL):
            os.remove(HELPER_PKL)
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
        if os.path.exists(HELPER_PKL):
            os.remove(HELPER_PKL)
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
@time_limit(5 * 60)
def chat_user(request):
    def get_chat_users_head(user_list):
        def chat_user_head(user):
            HELPER.get_head_img(user['user_name'], user['path'], user['name'])

        req_list = [(chat_user_head, (user,)) for user in user_list]
        parallel.run_thread_pool(req_list, is_lock=False)

    user_list = [{
        'name': user['RemarkName'] if user['RemarkName'] else user['NickName'],
        'path': os.path.join(MEDIA_HEAD_PATH, '%s.png' % re.subn(r'[\\\"\'/.*<>|:?]', '_', user['NickName'])[0]),
        'user_name': user['UserName']
        } for user in itchat.get_friends()]

    get_chat_users_head(user_list)
    return JsonResponse(dict(user_list=user_list, count=len(user_list)))



@csrf_exempt
@post_allowed_only
@async_to_sync
async def chat_send(request):
    '主动发送消息'
    msg = request.POST['msg']
    user = request.POST['user']
    await HELPER.send(msg, user)
    return JsonResponse(dict(res=True, msg=''))


@csrf_exempt
@post_allowed_only
@async_to_sync
async def chat_history(request):
    '获取历史消息'
    # @async_utils.async_wrap()
    async def history(user):
        for message in Message.objects.filter(robot=HELPER.robot).filter(user=user):
            await message.send_to_client()

    user = request.POST['user']
    await history(user)
    await HELPER.logger.info('读取与用户%s的聊天记录' % user)
    return JsonResponse(dict(res=True, msg=''))


# 设置api
def get_setting(request):
    item_list = HELPER.robot.settings.json()
    bool_list = [
        {
            'name': name,
            'val': val
        }
        for name, val in item_list.items()
        if isinstance(val, bool)
    ]
    text_list = []
    select_list = []
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
            settings = json.loads(request.body.decode())
            HELPER.robot.settings.change_settings(settings)
            await HELPER.logger.info('设置修改成功')
            return JsonResponse({'res': True, 'msg': '修改成功'})
        except EXCEPTIONS as error:
            await HELPER.logger.info(error)
            return JsonResponse({'res': False, 'msg': '修改失败'})
