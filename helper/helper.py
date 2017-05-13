# _*_ coding: utf-8 _*_
'小助手'
import os
import re
import time
import json
import threading
import requests
import itchat
import lxml
from django.db.utils import IntegrityError
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup as Bs
from channels import Group
from .base import EXCEPTIONS, info, get_now_week, error_report, TIMEOUT, TL_KEY, pkl_path
from .wheel import parallel as pl
from .models import Helper_user, Course, Weekday, Coursetime

class Helper(object):
    '助手类'
    keep_alive_name = None
    robot = None

    def __init__(self):
        self.IS_LOGIN = False
        self.settings = Setting()

    @staticmethod
    def get_head_img(user):
        '获取用户头像'
        if isinstance(user, itchat.storage.templates.User):
            user_name = user['UserName']
            nick_name = user['NickName']
            pic_dir = pic_dir = 'static/head/%s.png' % nick_name
            if not os.path.exists(pic_dir) or (time.time() - os.path.getctime(pic_dir) > 24*60*60):
                itchat.get_head_img(userName=user_name, picDir=pic_dir)
                Group('head').send({'text':json.dumps(dict(img_path=pic_dir, nick_name=nick_name))})


    @staticmethod
    def send(msg, user=None):
        '搜索用户并发送, 默认发给自己'
        def get_user_name(user):
            '自动处理  获取用户名'
            if isinstance(user, dict):
                if 'UserName' in user.keys():
                    return user['UserName']

            elif isinstance(user, Helper_user):
                return user.wx_UserName

            elif isinstance(user, str):
                if '@' in user:
                    return user
                else:
                    if itchat.search_friends(nickName=user):
                        return itchat.search_friends(nickName=user)[0]['UserName']
                    elif itchat.search_friends(name=user):
                        return itchat.search_friends(name=user)[0]['UserName']
            else:
                return None
        #send函数主体
        try:
            user_name = get_user_name(user)
            itchat.send(msg, user_name)
        except EXCEPTIONS as error:
            info(error)

    @staticmethod
    def get_robot_response(msg):
        '这里我们就像在“3. 实现最简单的与图灵机器人的交互”中做的一样'
        # 构造了要发送给服务器的数据
        apiUrl = 'http://www.tuling123.com/openapi/api'
        data = {
            'key'    : TL_KEY,
            'info'   : msg,
            'userid' : 'wechat-robot',
        }
        try:
            response = requests.post(apiUrl, data=data).json()
            # 字典的get方法在字典没有'text'值的时候会返回None而不会抛出异常
            return response.get('text')
        # 为了防止服务器没有正常响应导致程序异常退出，这里用try-except捕获了异常
        # 如果服务器没能正常交互（返回非json或无法连接），那么就会进入下面的return
        except EXCEPTIONS:
            # 将会返回一个None
            return

    
    def search_list(self, user_name=None):
        '在用户列表中查找当前用户是否已经绑定'
        if user_name:
            # try:
            user = Helper_user.objects.filter(robot=self.robot).filter(user_name=user_name)
            if user:
                return user[0]
            else:
                info('尚未绑定', True)
        else:
            return Helper_user.objects.filter(robot=self.robot)

    def wxname_update(self):
        '更新用户名, 在登陆时调用'
        for user in self.search_list():
            user.wx_UserName = itchat.search_friends(remarkName=user.user_name)[0]['UserName']
            user.save()
        self.keep_alive_name = itchat.search_mps(name='微信支付')[0]['UserName']

    def update_info(self, user=None):
        '更新用户信息'
        if user and isinstance(user, Helper_user):
            count = 0
            while True:
                try:
                    sep = UCASSEP(user.user_id, user.password)
                    user.user_name = sep.user_name
                    user.wx_UserName = itchat.search_friends(name=user.user_name)[0]['UserName']
                    user.nick_name = itchat.search_friends(name=user.user_name)[0]['NickName']
                    user.robot = self.robot
                    user.set_alias()
                    user.courses_update(sep.get_course_list())
                    user.remind_update(
                        get_now_week(),
                        self.settings.FLEXIBLE,
                        self.settings.FLEXIBLE_DAY
                        )
                    user.save()
                    info('更新成功, 尝试%d次' % (count + 1))
                    break
                except EXCEPTIONS as error:
                    if count < 5:
                        count += 1
                    else:
                        error_report(error, user)
        else:
            for user in self.search_list():
                self.update_info(user)
            self.settings.LAST_UPDATE = time.time()

    def add_user(self, now_user, user_name, text):
        '新增提醒用户'
        try:    #如果用户已经存在, 回报告并返回, 不存在会报错, 但被pass, 进入下一个try
            user = self.search_list(user_name)
            self.send('你已经绑定过啦', now_user)
            return
        except EXCEPTIONS:
            pass
        try:
            result = re.findall(r'用户名[:：\s]*(.+?)\s*密码[:：\s]*(.+?)$', text)
            if result:
                user_id = result[0][0]
                password = result[0][1]
            else:
                raise IOError('输入格式错误, 请输入"绑定 用户名:***  密码:***"')
            user = Helper_user(
                user_name='temp',
                user_id=user_id,
                password=password,
                )
            user.save()
            self.update_info(user)
            self.send('绑定成功', now_user)
        except EXCEPTIONS as error:
            if user:
                user.delete()
            error_report(error, now_user)

    def change_user(self, now_user, user_name, text):
        '修改用户信息'
        try:
            user = self.search_list(user_name)
            if '用户名' in text:
                user_ids = re.findall(r'用户名[:：\s]*(.*?)(\s*|\s+\S*\s*?)$', text)
                if user_ids:
                    user.user_id = user_ids[0][0]
                else:
                    raise IOError('输入格式错误, 请输入"绑定 用户名:***"')
            if '密码' in text:
                passwords = re.findall(r'密码[:：\s]*(.*?)(\s*|\s+\S*\s*?)$', text)
                if passwords:
                    user.password = passwords[0][0]
                else:
                    raise IOError('输入格式错误, 请输入"绑定 密码:***"')
            self.update_info(user)
            self.send('修改绑定信息成功', now_user)
        except EXCEPTIONS as error:
            error_report(error, now_user)

    def del_user(self, now_user, user_name):
        '删除用户'
        try:
            user = self.search_list(user_name=user_name)
            user.delete()
            self.send('取消绑定成功', now_user)
        except EXCEPTIONS as error:
            error_report(error, now_user)

    def cancel_remind(self, now_user, user_name):
        '取消提醒'
        user = self.search_list(user_name)
        user.is_open = False
        user.save()
        self.send('取消提醒成功', now_user)

    def remind(self, now_user=None, user_name=None):
        '定时提醒'
        def remind_main(user):
            '对某个个用户进行提醒的操作'
            try:
                user.remind_update(
                    get_now_week(),
                    self.settings.FLEXIBLE,
                    self.settings.FLEXIBLE_DAY
                    )
                if user.remind_time - self.settings.REMIND_BEFORE * 60 <= 0:       #当提醒时间到, 主动提醒一次
                    if not user.have_remind:                    #当没有提醒过
                        today = time.localtime().tm_wday
                        course = Course.objects.get(ident=user.remind)
                        coursetime = course.coursetimes.all().filter(weekday__index__exact=today)[0]
                        msg = '今天{}在{}上{}, 不要迟到哦'.format(
                            coursetime.show_start_time(),
                            course.place,
                            course.name
                            )
                        info(msg)
                        self.send(msg, user)

                        user.have_remind = True                 #修改为已经提醒过
                        user.save()
                else:                                           #没有到提醒时间
                    if user.have_remind:
                        user.have_remind = False
                        user.save()
            except EXCEPTIONS as error:
                info(error)

        def remind_thread():
            '以执行新线程的方式循环提醒'
            time.sleep(int(self.settings.REMIND_WAIT * 60))
            info('打开新线程:%d, 提醒间隔%d分%d秒' %
                 (pl.get_tid(), self.settings.REMIND_WAIT//1, self.settings.REMIND_WAIT%1*60))
            try:
                if time.time() - self.settings.LAST_UPDATE > self.settings.UPDATE_WAIT * 60:
                    self.update_info()
                    self.keep_alive()
                for user in self.search_list():
                    if user.is_open:
                        remind_main(user)
            except EXCEPTIONS as error:
                info(error)

            try:                #继续打开新线程
                self.remind()
                return
            except EXCEPTIONS as error:
                info(error)
                info('打开新线程失败, 自动提醒结束')
                self.settings.REMIND_ALIVE = False
                return
        #remind函数主体
        if user_name and now_user:
            user = self.search_list(user_name)
            user.is_open = True
            user.save()
            self.send('打开提醒成功', now_user)

        else:
            # try:
            if self.settings.REMIND_ALIVE:
                threading.Thread(target=remind_thread, args=(), name='remind', daemon=True).start()
                # new_thread.start()
                # pl.run_thread_pool([(remind_thread, ())], False)
            # except EXCEPTIONS as error:
            #     info(error)

    def remind_list_update(self, user_name=None, user=None):
        '手动更新信息, 允许外部调用'
        try:
            if user and isinstance(user, Helper_user):
                user.remind_update(
                    get_now_week(),
                    self.settings.FLEXIBLE,
                    self.settings.FLEXIBLE_DAY
                    )
            elif user_name and isinstance(user_name, str):
                self.search_list(user_name).remind_update(
                    get_now_week(),
                    self.settings.FLEXIBLE,
                    self.settings.FLEXIBLE_DAY
                    )
            #被外部调用
            else:
                for _user in self.search_list():
                    self.remind_list_update(user=_user)

        except EXCEPTIONS as error:
            error_report(error)

    def my_help(self, now_user, keys):
        '显示帮助'
        msg = '功能有: ' + ', '.join([', '.join(each) for each in keys])
        self.send(msg, now_user)
        self.send('相信你看名字就会用了', now_user)

    def show_course_list(self, now_user, user_name, is_pic=True, is_with_num=False):
        '显示课表'
        def get_course_list_pic(pic_path, user):
            '生成图片'
            def get_time_table(user):
                '转换课表为矩阵形式'
                week = get_now_week()
                table = [
                    [
                        user.courses.all().filter(
                            **{
                                'coursetimes__weekday__index': weekday,
                                'coursetimes__start__lte': num,
                                'coursetimes__end__gte': num,
                                'end_week__gte': week,
                                'start_week__lte': week,
                            }).values('name')
                        for num in range(12)
                    ]
                    for weekday in range(7)
                ]
                return table

            def draw_font(col, row, text, color=(0, 0, 0), indent=0.5):
                '打印第row行col列的字, 根据该块大小和字数进行分行打印, 调整应该打印的位置'
                #自动计算调整参数
                line_max = int((width_list[col + 1] - width_list[col]) / font_size - indent * 2)
                if len(text) % line_max:
                    line_num = len(text) // line_max + 1
                else:
                    line_num = len(text) // line_max
                font_x = width_list[col] + indent * font_size
                font_y = height_list[row] + (height_list[row + 1] - height_list[row] - \
                (font_size + space) * line_num + space) / 2
                #分行打印
                for num in range(line_num):
                    line = text[num * line_max : (num + 1) * line_max]
                    if line != '':
                        draw.text(
                            (font_x, font_y + num * (font_size + space)),
                            line, font=font, fill=color
                            )

            ori_pic_path = 'static/course_png/course.png'
            from_begin = False if os.path.exists(ori_pic_path) else True

            #颜色
            line_color = (221, 221, 221)
            white = (255, 255, 255)
            grey_0 = (245, 245, 245)
            grey_1 = (204, 204, 204)
            blue_0 = (225, 234, 240)
            blue_1 = (0, 136, 205)

            #图像和字体大小
            space = 5
            font_size = 14
            width = 900
            height = 800

            if from_begin:
                img = Image.new('RGB', (width, height), white)
            else:
                img = Image.open(ori_pic_path)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype('static/fonts/Deng.ttf', font_size, encoding='utf-8')
            table = get_time_table(user)

            part_w = 7
            part_h = 12
            _change = font_size * 7
            _width = width - _change
            width_list = [0] + [num + _change for num in range(0, _width, int(_width/part_w))]
            height_list = [num for num in range(0, height, int(height/part_h))]
            width_list[-1] = width
            height_list[-1] = height
                # 初始图片
                # 划块填色
            if from_begin:
                for index_w, num_w in enumerate(width_list):
                    for index_h, num_h in enumerate(height_list):
                        if not index_h or not index_w:
                            continue
                        #第一行第一列
                        elif index_h is 1 and index_w is 1:
                            draw.rectangle([0, 0, num_w, num_h], grey_1, line_color)
                        #第一行
                        elif index_h is 1 and index_w is not 1:
                            width_last = width_list[index_w - 1]
                            draw.rectangle([width_last, 0, num_w, num_h], grey_1, line_color)
                        #第一列
                        elif index_w is 1 and index_h is not 1:
                            height_last = height_list[index_h - 1]
                            draw.rectangle([0, height_last, num_w, num_h], blue_0, line_color)
                        #主体
                        else:
                            height_last = height_list[index_h - 1]
                            width_last = width_list[index_w - 1]
                            #偶数行
                            if not index_h % 2:
                                draw.rectangle(
                                    [width_last, height_last, num_w, num_h], grey_0, line_color
                                    )
                            #奇数行
                            else:
                                draw.rectangle(
                                    [width_last, height_last, num_w, num_h], white, line_color
                                    )

                #画字
                draw_font(0, 0, "节次/星期")
                for num in range(7):
                    draw_font(num + 1, 0, Weekday.objects.get(index=num).day)
                for num in range(1, 12):
                    draw_font(0, num, '第%d节'%num)

                img.save(ori_pic_path, 'png')

            for i in range(7):
                for j in range(11):
                    try:
                        draw_font(i + 1, j, table[i][j][0]['name'], blue_1)
                    except EXCEPTIONS:
                        pass
            #保存
            img.save(pic_path, 'png')
        #show_course_list函数主体
        try:
            user = self.search_list(user_name)
            if is_pic:
                self.send('正在获取课表, 请稍候', now_user)
                pic_path = 'static/course_png/%s.course.png' % user.wx_UserName
                get_course_list_pic(pic_path, user)
                self.send('@img@' + pic_path, now_user)
                os.remove(pic_path)
            else:
                course_everyday = [
                    user.courses.all().filter(coursetimes__weekday__index=weekday)
                    for weekday in range(7)
                    ]
                msg_list = list()
                for weekday, course_the_day in enumerate(course_everyday):
                    day = Weekday.objects.get(index=weekday)
                    for course in course_the_day:
                        coursetime = course.coursetimes.all().filter(weekday=day)[0]
                        course_num = ' '.join(list(map(
                            str,
                            range(coursetime.start, coursetime.end+1)
                            )))
                        if not is_with_num:
                            msg_list.append('{}, {}, {}, 第{}节'.format(
                                course.name,
                                course.place,
                                coursetime.weekday,
                                course_num
                            ))
                        else:
                            msg_list.append('{}, {}, {}, 第{}节, 编号:{}'.format(
                                course.name,
                                course.place,
                                coursetime.weekday,
                                course_num,
                                course.ident
                            ))
                msg = '\n'.join(msg_list)
                self.send(msg, now_user)
        except EXCEPTIONS as error:
            error_report(error, now_user)

    def show_remind_list(self, now_user, user_name):
        '显示提醒时间'
        try:
            user = self.search_list(user_name)
            user.remind_update(
                get_now_week(),
                self.settings.FLEXIBLE,
                self.settings.FLEXIBLE_DAY
                )
            course = Course.objects.get(ident=user.remind)
            msg = '%s离下节课%s上课还有%d天%d小时%d分%d秒, 上课地点在%s' % (
                user.nick_name,
                course.name,
                abs(user.remind_time) // (24 * 60 * 60),
                (abs(user.remind_time) % (24 * 60 * 60)) // (60 * 60),
                (abs(user.remind_time) % (60 * 60)) //60,
                abs(user.remind_time) % 60,
                course.place
            )
            # print(msg)
            self.send(msg, now_user)
        except EXCEPTIONS as error:
            error_report(error)
    #选退课功能暂时关闭
        # def add_course(self, now_user, nick_name, text):
        #     '按课程编号选课'
        #     try:
        #         user = self.search_list(nick_name)
        #         if '编号' in text:
        #             num = re.findall(r'编号[:：\s]*(.*?)\s*$', text)[0]
        #         else:
        #             raise IOError('输入格式错误, 应为"选课 编号:***", 你可以输入"编号"查看已选课程编号')
        #         sep = UCASSEP(user.user_id, user.password)
        #         sep.get_course_list()
        #         if sep.add_course(num):
        #             self.send('选课成功', now_user)
        #         else:
        #             self.send('选课失败', now_user)
        #     except EXCEPTIONS as error:
        #         error_report(error)

        # def drop_course(self, now_user, nick_name, text):
        #     '按课程编号退课'
        #     try:
        #         user = self.search_list(nick_name)
        #         if '编号' in text:
        #             num = re.findall(r'编号[:：\s]*(.*?)\s*$', text)[0]
        #         else:
        #             raise IOError('输入格式错误, 应为"退课 编号:***", 你可以输入"编号"查看已选课程编号')
        #         sep = UCASSEP(user.user_id, user.password)
        #         sep.get_course_list()
        #         if sep.drop_course(num):
        #             self.send('退课成功', now_user)
        #         else:
        #             self.send('退课失败', now_user)
        #     except EXCEPTIONS as error:
        #         error_report(error)

    def logout(self):
        '退出登陆'
        self.settings.__init__()
        self.IS_LOGIN = False
        self.robot = None
        thread_remind = pl.search_thread(name='remind', part=True)
        if thread_remind:
            pl.kill_thread(thread=thread_remind)
            info('remind线程已关闭')
        itchat.logout()
        if os.path.exists(pkl_path):
            os.remove(pkl_path)

    def keep_alive(self):
        '保活'
        Helper.send('1', self.keep_alive_name)

class Setting(object):
    '小助手设置'
    trans_dict = dict(
        REMIND_ALIVE='提醒开关',
        ROBOT_REPLY='智能回复开关',
        VOICE_REPLY='语音回复开关',
        REMIND_WAIT='提醒间隔',
        REMIND_BEFORE='提醒提前时间',
        UPDATE_WAIT='信息更新间隔',
        LAST_UPDATE='上次更新时间',
        FLEXIBLE='灵活调整开关',
        FLEXIBLE_DAY='灵活调整日期'
    )
    def __init__(self):
        '设置参数初始化'
        self.REMIND_ALIVE = True
        self.ROBOT_REPLY = True
        self.VOICE_REPLY = True
        self.REMIND_WAIT = 2#分钟
        self.REMIND_BEFORE = 30#分钟
        self.UPDATE_WAIT = 60#分钟
        self.LAST_UPDATE = 0
        self.FLEXIBLE = False
        self.FLEXIBLE_DAY = 0

    def __str__(self):
        return '\n'.join(
            ['%s:%s' % (self.trans_to_chinese(name), value)
             for name, value in self.trans_to_dict().items()]
        )

    def trans_to_dict(self):
        return vars(self)

    def trans_to_chinese(self, name):
        '转化为中文显示'
        return self.trans_dict[name]

    def trans_flexible_day(self, weekday=None):
        '将灵活调整日期换为数字 或 将数字化为日期'
        if not weekday:
            return Weekday.objects.get(index=self.FLEXIBLE_DAY).day
        else:
            self.FLEXIBLE_DAY = Weekday.objects.get(day=weekday).index

    def change_settings(self, items):
        self.VOICE_REPLY = items['VOICE_REPLY']
        self.UPDATE_WAIT = items['UPDATE_WAIT']
        self.REMIND_ALIVE = items['REMIND_ALIVE']
        self.REMIND_BEFORE = items['REMIND_BEFORE']
        self.REMIND_WAIT = items['REMIND_WAIT']
        self.ROBOT_REPLY = items['ROBOT_REPLY']
        self.FLEXIBLE = items['FLEXIBLE']
        self.trans_flexible_day(items['FLEXIBLE_DAY'])
        self.remind_change()
        info("修改设置 %s" % items)

    def remind_change(self):
        '根据REMIND_ALIVE打开或者关闭提醒'
        thread_remind = pl.search_thread(name='remind', part=True)
        if self.REMIND_ALIVE:
            if not thread_remind:
                from .base import HELPER
                HELPER.remind()
                info('打开remind线程')
        else:
            if thread_remind:
                pl.kill_thread(thread=thread_remind)
                info('关闭remind线程')

class UCASSEP(object):
    'UCAS SEP系统'
    user_id = ''
    password = ''
    user_name = ''
    course_list = None
    session = requests.Session()
    is_login = False
    is_course = False
    temp_page = ''

    def _get(self, url, data=None, empty_post_tag=False):
        try:
            if data is None and empty_post_tag is False:
                response = self.session.get(url=url, timeout=TIMEOUT)
            else:
                response = self.session.post(url=url, data=data, timeout=TIMEOUT)
            if response.status_code is 200:
                return response
            else:
                response.raise_for_status()
        except EXCEPTIONS as error:
            info(error, True)

    def _get_json(self, url, data=None, empty_post_tag=False):
        try:
            response = self._get(url, data, empty_post_tag)
            return response.json()
        except EXCEPTIONS:
            info('该网页返回的不是json数据', True)

    def _get_page(self, url, data=None, empty_post_tag=False):
        try:
            response = self._get(url, data, empty_post_tag)
            return Bs(response.text, 'html.parser')
        except EXCEPTIONS:
            info('无法解析该网页', True)

    def __init__(self, user_id, password):
        try:
            self.session.headers.update({
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest',
                })
            self.user_id = user_id
            self.password = password
            self.login()
            self.login_course()
        except EXCEPTIONS as error:
            info('用户信息错误, {}'.format(error), True)

    def login(self):
        '登陆'
        data = {
            'username': self.user_id,
            'password': self.password,
            'remember': 'checked'
            }
        url = 'http://onestop.ucas.ac.cn/Ajax/Login/0'
        try:
            result = self._get_json(url=url, data=data)
            if result['f'] is True:
                self.is_login = True
                soup = self._get_page(result['msg'])
                self.temp_page = result['msg']
                self.user_name = str(soup.find('li', 'btnav-info').contents[0])\
                    .replace('\r', '').replace('\n', '').replace('\t', '').replace(' ', '')\
                    .replace(u'\x80', '').replace(u'\x90', '').replace(u'\xa0', ' ')
                info('%s登陆成功' % self.user_name)
            else:
                raise NotImplementedError(result['msg'])
        except EXCEPTIONS as error:
            info(error, True)

    def logout(self):
        '退出登陆'
        url = 'http://sep.ucas.ac.cn/logout?o=platform'
        self._get(url=url)
        self.is_login = False
        info('{}退出登陆'.format(self.user_name))

    def login_course(self):
        '登陆至选课系统'
        if self.is_login is False:
            info('尚未成功登陆SEP')
            self.login()
        else:
            if not self.is_course:
                try:
                    url = 'http://sep.ucas.ac.cn/portal/site/226/821'
                    soup = self._get_page(url)
                    reDirUrl = soup.find('h4').contents[1].get('href')
                    self._get(reDirUrl)
                    self.is_course = True
                except EXCEPTIONS:
                    self.is_login = False
                    self.is_course = False
                    info('登陆SEP系统失效, 重新登陆')
                    self.login()

    def is_chosen(self, course):
        '查看该课程是否已经选上'
        if not isinstance(course, str):
            course = str(course)
        if not self.course_list:
            self.get_course_list()
        for item in self.course_list:
            if item['num'] == course:
                info('{}已经选上'.format(item['name']))
                result = True
                break
        else:
            info('编号为{}的课程未选上'.format(course))
            result = False
        return result

    def add_course(self, course):
        '选课'
        if self.is_chosen(course):
            return True
        else:
            data = {
                'deptIds':'910',
                'sids':course
            }
            url = 'http://jwxk.ucas.ac.cn/courseManageBachelor/saveCourse?s='
            try:
                soup = self._get_page(url=url, data=data)
                if str(soup.find('title').contents[0]).find('Apache Tomcat') is not -1:
                    raise NotImplementedError('尚未开放选课, 或课程编号' + course + '有误')
                if len(soup.find('label', 'success').contents) is not 0:
                    info(soup.find('label', 'success').contents[0])
                    return True
                elif len(soup.find('label', 'error').contents) is not 0:
                    info(soup.find('label', 'error').contents[0])
                    return False
                else:
                    raise NotImplementedError('获取选课结果时出现异常错误')
            except EXCEPTIONS as error:
                info(error)
                return False

    def drop_course(self, course):
        '退课'
        if self.is_chosen(course):
            url = 'http://jwxk.ucas.ac.cn/courseManageBachelor/del/' + course + '?s='
            try:
                soup = self._get_page(url)
                if len(soup.find('label', 'success').contents) is not 0:
                    info(soup.find('label', 'success').contents[0])
                    return True
                elif len(soup.find('label', 'error').contents) is not 0:
                    info(soup.find('label', 'error').contents[0])
                    return False
                else:
                    raise NotImplementedError('获取退课结果时出现异常错误')
            except EXCEPTIONS as error:
                info(error)
                return True
        else:
            info('课程未选上, 无法退课')
            return False

    def save_course(self, num):
        '储存指定课程'
        def get_course_detail(num):
            '获取指定课程的具体信息'
            link = 'http://jwxk.ucas.ac.cn/course/coursetime/' + str(num)
            tree = lxml.etree.HTML(self.session.get(url=link).content)
            if tree.xpath('//title/text()')[0] != '课程时间地点信息-选课系统'\
            or not tree.xpath('//th'):
                return None
            name = (tree.xpath('//p/text()'))[0][5:]
            place = tree.xpath('//th[text()="上课地点"]/../td/text()')[0]
            times = [(re.findall(r'(星期.?)：', each)[0], re.findall(r'(\d*)[、节]', each))
                     for each in tree.xpath('//th[text()="上课时间"]/../td/text()')]
            weeks_temp = tree.xpath('//th[text()="上课周次"]/../td/text()')[0].split('、')
            weeks = (int(weeks_temp[0]) - 1, int(weeks_temp[-1]) - 1)
            return dict(name=name, weeks=weeks, place=place, times=times)

        try:
            courese = get_course_detail(num)
            if not courese:
                info('不存在编号%d对应的课程' % num)
                return

        except EXCEPTIONS as error:
            info(error)
            return

        try:
            new_course = Course.objects.create(ident=num)
        except IntegrityError:
            new_course = Course.objects.get(ident=num)
            if new_course.place:
                info('编号为%d的课程已经存在' % num)
                return

        for times in courese['times']:
            try:
                coursetime = Coursetime.objects.get(
                    weekday=Weekday.objects.get(day=times[0]),
                    start=int(times[1][0]),
                    end=int(times[1][-1])
                    )
            except Coursetime.DoesNotExist:
                coursetime = Coursetime.objects.create(
                    weekday=Weekday.objects.get(day=times[0]),
                    start=int(times[1][0]),
                    end=int(times[1][-1])
                )
            new_course.coursetimes.add(coursetime)
        new_course.start_week, new_course.end_week = courese['weeks'][0], courese['weeks'][1]
        new_course.name = courese['name']
        new_course.place = courese['place']
        new_course.save()

    def get_course_list(self):
        '获取已选择课程, 并储存'
        self.course_list = list()
        url = 'http://jwxk.ucas.ac.cn/courseManageBachelor/main'
        soup = self._get_page(url)
        tbody = soup.find('tbody').findChildren()
        pattern = re.compile(r'/course/coursetime/(\d*)')
        for i in range(int(len(tbody)/15)):
            if '退课成功' not in tbody[i*15+14].get_text():
                href = tbody[i*15 + 4]['href']
                num = re.findall(pattern, href)[0]
                if not Course.objects.filter(ident=num).count():
                    self.save_course(num)
                self.course_list.append(num)
        info('%s 课表获取成功' % self.user_name)
        return self.course_list
