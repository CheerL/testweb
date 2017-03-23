# _*_ coding: utf-8 _*_
'小助手'
import os
import re
import time
from ast import literal_eval
import datetime
import requests
import itchat
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from .wheel import parallel as pl
from .SEP import UCASSEP
from . import EXCEPTIONS, info, WEEK, TIMEOUT, pkl_dir, Helper_User

TL_KEY = '71f28bf79c820df10d39b4074345ef8c' #图灵机器人密钥
REMIND_WAIT = 1#分钟
REMIND_BEFORE = 30#分钟
AUTO_UPDATE = 60#分钟
A_WEEK = 60 * 60 * 24 * 7#秒
END_WEEK = 20
FILE_NAME = 'static/data.csv'
WEEK_DICT = dict(map(lambda x, y: [x, y], WEEK, [i for i in range(7)]))
COURSE_NUM = [str(i) for i in range(1, 12)]
COURSE_DICT = dict(map(lambda x, y: [x, y], COURSE_NUM, (
    [8, 30], [9, 20], [10, 30], [11, 20],
    [13, 30], [14, 20], [15, 30], [16, 20],
    [19, 00], [19, 50], [20, 50]
    )))

class Helper(object):
    '助手类'
    is_login = False
    is_wait = False
    is_run = False
    user_list = None
    remind_alive = True
    remind_tid = None
    robot_reply = True
    host = None
    admin = None
    admin_report = False
    last_update = 0

    def init(self):
        '所有参数修改为初始值, 结束remind进程'
        self.is_login = self.is_wait = self.is_run = self.admin_report = False
        self.robot_reply = self.remind_alive = True
        self.host = self.admin = None
        self.last_update = 0
        if pl.search_thread('remind'):
            pl.kill_thread(tid=self.remind_tid)
            time.sleep(1)
            info('线程已关闭')

    @staticmethod
    def get_now_week():
        '返回当前周次'
        BEG = 51
        NOW = time.localtime().tm_yday
        return (NOW - BEG) // 7

    @staticmethod
    def get_course_time(day, num):
        '获取该课对应的时间'
        if day in WEEK:
            wday = WEEK_DICT[day]
        else:
            raise NotImplementedError('输入的课程日期有误')
        if num in COURSE_NUM:
            course_time = COURSE_DICT[num]
        else:
            raise NotImplementedError('输入的课程节次有误')
        now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        delta = datetime.timedelta(
            days=wday - time.localtime().tm_wday,
            hours=course_time[0], minutes=course_time[1]
            )
        return time.mktime(datetime.datetime.timetuple(now + delta))

    @staticmethod
    def __show_remind_list(nick_name, remind_list):
        '显示提醒时间'
        if remind_list:
            name = remind_list[0][0]
            place = remind_list[0][1]
            delta = time.time() - remind_list[0][2]
            day = abs(delta) // (24 * 60 * 60)
            hour = (abs(delta) % (24 * 60 * 60)) // (60 * 60)
            mins = (abs(delta) % (60 * 60)) //60
            sec = abs(delta) % 60
            is_pass = '离下节课%s上课还有' % name if delta < 0 else '迟到了, %s已经上课' % name
            return ('%s%s%d天%d小时%d分%d秒, 上课地点在%s' %
                    (nick_name, is_pass, day, hour, mins, sec, place), delta)
        else:
            raise NotImplementedError('提醒项目为空')
    @staticmethod
    def my_error(error, user=None, up_rep=True):
        '错误处理, 向用户发送错误信息或继续上报错误'
        info(error)
        if up_rep:
            raise NotImplementedError(error)
        else:
            Helper.send(str(error), user)

    @staticmethod
    def send(msg, user=None):
        '搜索用户并发送, 默认发给自己'
        def get_user_name(user):
            '自动处理  获取用户名'
            if user:
                if isinstance(user, dict):
                    if 'UserName' in user.keys():
                        return user['UserName']

                elif isinstance(user, Helper_User):
                    if itchat.search_friends(nickName=user.nick_name):
                        return itchat.search_friends(nickName=user.nick_name)[0]['UserName']

                elif isinstance(user, str):
                    if '@' in user:
                        return user
                    else:
                        if itchat.search_friends(name=user):
                            return itchat.search_friends(name=user)[0]['UserName']
            return None

        try:
            user_name = get_user_name(user)
            itchat.send(msg, user_name)
        except EXCEPTIONS as error:
            info(error)

    @staticmethod
    def get_response(msg):
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

    def __init__(self):
        '初始化'
        if os.path.isfile(FILE_NAME) and os.path.getsize(FILE_NAME) > 100:
            temp = pd.read_csv(FILE_NAME).fillna(value=False).T
            for i in temp:
                item = temp[i]
                if isinstance(item['course_list'], str) and isinstance(item['remind_list'], str):
                    item['course_list'] = literal_eval(item['course_list'])
                    item['remind_list'] = literal_eval(item['remind_list'])

            self.user_list = [temp[num].to_dict() for num in temp]
        else:
            self.user_list = list()

    def search_list(self, nick_name=None):
        '在用户列表中查找当前用户是否已经绑定'
        if nick_name:
            try:
                return Helper_User.objects.get(nick_name=nick_name)
            except EXCEPTIONS:
                raise NotImplementedError('尚未绑定')
        else:
            return Helper_User.objects.all()

    def update_info(self, user=None):
        '更新用户信息'
        if user and isinstance(user, Helper_User):
            count = 0
            while True:
                try:
                    sep = UCASSEP(user.user_id, user.password)
                    sep.get_course_list()
                    user.user_name = sep.user_name
                    user.course_list = sep.course_list
                    user.save()
                    info('更新成功, 尝试%d次' % (count + 1))
                    break
                except EXCEPTIONS as error:
                    if count < 5:
                        count += 1
                    else:
                        self.my_error(error, user)
        else:
            for user in self.search_list():
                self.update_info(user)
            self.last_update = time.time()

    def add_user(self, now_user, nick_name, text):
        '新增提醒用户'
        try:    #如果用户已经存在, 回报告并返回, 不存在会报错, 但被pass, 进入下一个try
            user = self.search_list(nick_name)
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
            user = Helper_User.objects.create(
                nick_name=nick_name,
                user_id=user_id,
                password=password,
                is_open=True,
                have_remind=False
                )
            self.update_info(user)
            self.send('绑定成功', now_user)
        except EXCEPTIONS as error:
            if user:
                user.delete()
            self.my_error(error, now_user)

    def change_user(self, now_user, nick_name, text):
        '修改用户信息'
        try:
            user = self.search_list(nick_name)
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
            self.my_error(error, now_user)

    def del_user(self, now_user, nick_name):
        '删除用户'
        try:
            for user in Helper_User.objects.filter(nick_name=nick_name):
                user.delete()
            self.send('取消绑定成功', now_user)
        except EXCEPTIONS as error:
            self.my_error(error, now_user)

    def cancel_remind(self, now_user, nick_name):
        '取消提醒'
        try:
            user = self.search_list(nick_name)
            user.is_open = False
            user.save()
            self.send('取消提醒成功', now_user)
        except EXCEPTIONS as error:
            self.my_error(error)

    def remind(self, now_user=None, nick_name=None, host=None):
        '定时提醒'
        def _remind_do(remind, user):
            _time = time.strftime('%H:%M', time.localtime(remind[2]))
            msg = '今天{}在{}上{}, 不要迟到哦'.format(_time, remind[1], remind[0])
            info(msg)
            self.send(msg, user)

        def _remind_main(user):
            self. __remind_list_update(user)
            nick_name = user.nick_name
            try:
                remind_list = literal_eval(user.remind_list)
                result = self.__show_remind_list(nick_name, remind_list)
                if result[1] > 0:                               #当上课时间到, 把课程清理出提醒队列
                    remind_list.pop(0)
                    self.__remind_list_update(user)
                elif result[1] + REMIND_BEFORE * 60 >= 0:       #当提醒时间到, 主动提醒一次
                    if not user.have_remind:                    #当没有提醒过
                        _remind_do(remind_list[0], user)        #提醒
                        user.have_remind = True                 #修改为已经提醒过
                else:                                           #没有到提醒时间
                    user.have_remind = False
                user.save()
            except EXCEPTIONS as error:
                self.my_error(error, user)

        def _remind():
            #time.sleep(1)
            self.remind_tid = pl.get_tid()
            info('打开新线程:%d, 提醒间隔%f分钟' % (self.remind_tid, REMIND_WAIT))
            time.sleep(int(REMIND_WAIT * 60))
            #self.remind_pid = pl.
            if time.time() - self.last_update > AUTO_UPDATE * 60:
                self.update_info()
            for user in self.search_list():
                if user.is_open:
                    _remind_main(user)
            info('成功提醒并保存')

            if not self.host:
                if host:
                    self.host = host
                else:
                    info('host不存在')

            error_count = 0
            while True:
                try:
                    requests.get('http://%s/app/remind' % self.host, timeout=TIMEOUT)
                    break
                except EXCEPTIONS as error:
                    info(error)
                    if error_count < 5:
                        error_count += 1
                        time.sleep(3)
                    else:
                        info('打开新线程失败, 自动提醒结束, 尝试%d次' % (error_count))
                        info(self.host)
                        self.remind_alive = False
                        return

        if self.get_now_week() > END_WEEK:
            self.remind_alive = False
            raise NotImplementedError('学期已经结束')

        if nick_name:
            user = self.search_list(nick_name)
            user.is_open = True
            user.save()
            self.send('打开提醒成功', now_user)

        else:
            try:
                info('remind %s' % self.remind_alive)
                if self.remind_alive:
                    pl.run_thread([(_remind, ())], 'remind', False)
            except EXCEPTIONS as error:
                info(error)

    def remind_list_update(self, nick_name=None, user=None):
        '手动更新信息'
        try:
            if user and isinstance(user, Helper_User):
                pass
            elif nick_name and isinstance(nick_name, str):
                user = self.search_list(nick_name)
            else:
                for _user in self.search_list():
                    self.remind_list_update(user=_user)
                return

            self.update_info(user)
            self.__remind_list_update(user)
        except EXCEPTIONS as error:
            self.my_error(error)

    def my_help(self, now_user, keys):
        '显示帮助'
        msg = '功能有: ' + ', '.join([', '.join(each) for each in keys])
        self.send(msg, now_user)
        self.send('相信你看名字就会用了', now_user)

    def show_course_list(self, now_user, nick_name, is_pic=True, is_with_num=False):
        '显示课表'
        try:
            user = self.search_list(nick_name)
            course_list = literal_eval(user.course_list)
            if is_pic:
                pic_name = 'static/%s.course.png' % nick_name
                self.__get_course_list_pic(pic_name, course_list)
                self.send('@img@' + pic_name, now_user)
                os.remove(pic_name)
            else:
                temp_course_list = list()
                for course in course_list:
                    para = [course['place'], course['name'], course['num']]
                    temp_course_list += [
                        (para[1], para[0], day, num, para[2]) for (day, num) in course['times']
                    ]
                temp_course_list.sort(key=lambda x: self.get_course_time(x[2], x[3][0]))
                if not is_with_num:
                    msg = '\n'.join(['{}, {}, {}, 第{}节'.format(
                        course[0], course[1], course[2],
                        '.'.join(course[3])) for course in temp_course_list])
                else:
                    msg = '\n'.join(['{}, {}, {}, 第{}节, 编号{}'.format(
                        course[0], course[1], course[2],
                        '.'.join(course[3]), course[4]) for course in temp_course_list])
                self.send(msg, now_user)
        except EXCEPTIONS as error:
            self.my_error(error, now_user)

    def show_remind_list(self, now_user, nick_name):
        '显示提醒时间'
        try:
            user = self.search_list(nick_name)
            remind_list = literal_eval(user.remind_list)
            result = self.__show_remind_list(nick_name, remind_list)
            self.send(result[0], now_user)
        except EXCEPTIONS as error:
            self.my_error(error)

    def add_course(self, now_user, nick_name, text):
        '按课程编号选课'
        try:
            user = self.search_list(nick_name)
            if '编号' in text:
                num = re.findall(r'编号[:：\s]*(.*?)\s*$', text)[0]
            else:
                raise IOError('输入格式错误, 应为"选课 编号:***", 你可以输入"编号"查看已选课程编号')
            sep = UCASSEP(user.user_id, user.password)
            sep.get_course_list()
            if sep.add_course(num):
                self.send('选课成功', now_user)
            else:
                self.send('选课失败', now_user)
        except EXCEPTIONS as error:
            self.my_error(error)

    def drop_course(self, now_user, nick_name, text):
        '按课程编号退课'
        try:
            user = self.search_list(nick_name)
            if '编号' in text:
                num = re.findall(r'编号[:：\s]*(.*?)\s*$', text)[0]
            else:
                raise IOError('输入格式错误, 应为"退课 编号:***", 你可以输入"编号"查看已选课程编号')
            sep = UCASSEP(user.user_id, user.password)
            sep.get_course_list()
            if sep.drop_course(num):
                self.send('退课成功', now_user)
            else:
                self.send('退课失败', now_user)
        except EXCEPTIONS as error:
            self.my_error(error)

    @staticmethod
    def __get_course_list_pic(pic_name, course_list):
        '生成图片'
        def get_time_table(course_list):
            '转换课表为矩阵形式'
            table = np.zeros((7, 11)).astype(str)
            for index, day in enumerate(WEEK):
                for num in range(1, 12):
                    for course in course_list:
                        week = Helper.get_now_week()
                        if week > int(course['weeks'][1]) or week < int(course['weeks'][0]):
                            continue
                        func = lambda x:\
                            True\
                            if list(filter(\
                                lambda x: True if x[0] == day and str(num) in x[1] else False,\
                                x['times']))\
                            else False
                        if func(course):
                            table[index, num - 1] = course['name']
            return table

        def draw_font(x, y, text, color=(0, 0, 0), indent=0.5):
            '打印第y行x列的字, 根据该块大小和字数进行分行打印, 调整应该打印的位置'
            #自动计算调整参数
            line_max = int((width_list[x + 1] - width_list[x]) / font_size - indent * 2)
            if len(text) % line_max:
                line_num = len(text) // line_max + 1
            else:
                line_num = len(text) // line_max
            font_x = width_list[x] + indent * font_size
            font_y = height_list[y] + (height_list[y + 1] - height_list[y] - \
            (font_size + space) * line_num + space) / 2
            #分行打印
            for num in range(line_num):
                line = text[num * line_max : (num + 1) * line_max]
                if line != '':
                    draw.text(
                        (font_x, font_y + num * (font_size + space)),
                        line, font=font, fill=color
                        )

        #颜色
        white = (255, 255, 255)
        grey_0 = (245, 245, 245)
        grey_1 = (204, 204, 204)
        blue_0 = (225, 234, 240)
        blue_1 = (0, 136, 205)
        line_color = (221, 221, 221)

        #图像和字体大小
        space = 5
        font_size = 14
        width = 900
        height = 800

        img = Image.new('RGB', (width, height), white)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('static/Deng.ttf', font_size, encoding='utf-8')
        table = get_time_table(course_list)

        part_w = 7
        part_h = 12
        _change = font_size * 7
        _width = width - _change
        width_list = [0] + [num + _change for num in range(0, _width, int(_width/part_w))]
        height_list = [num for num in range(0, height, int(height/part_h))]
        width_list[-1] = width
        height_list[-1] = height

        #划块填色
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
        for num, day in enumerate(WEEK):
            draw_font(num + 1, 0, day)
        for num in range(1, 12):
            draw_font(0, num, '第%d节'%num)
        for i in range(7):
            for j in range(11):
                if table[i, j] != '0.0':
                    draw_font(i + 1, j + 1, table[i, j], blue_1)
        #保存
        img.save(pic_name, 'png')

    def __remind_list_update(self, user):
        '更新提醒列表'
        def _remind_list_update_main(week, course_list, count=0):
            if week + count > END_WEEK:
                user.is_open = False
                user.save()
                raise NotImplementedError('%s本学期已经没有课了' % (user['nick_name']))
            while not course_list:
                try:
                    self.update_info(user)
                    course_list = literal_eval(user.course_list)
                except EXCEPTIONS:
                    pass

            now = time.time()
            remind_list = list()
            for course in course_list:
                place = course['place']
                name = course['name']
                remind_list += [(name, place, self.get_course_time(day, num[0]) + A_WEEK * count)
                                for (day, num) in course['times']
                                if week <= int(course['weeks'][1])
                                and week >= int(course['weeks'][0])]
            remind_list = list(filter(lambda x: x[2] > now, remind_list))
            if remind_list:
                remind_list.sort(key=lambda x: x[2])
                user.remind_list = remind_list
                user.save()
            else:
                return _remind_list_update_main(week, course_list, count + 1)

        course_list = literal_eval(user.course_list)
        week = self.get_now_week()
        _remind_list_update_main(week, course_list)

    def logout(self):
        '退出登陆'
        self.init()
        itchat.logout()

    def check_login(self):
        '热登陆检查'
        if not itchat.instanceList[0].alive:
            if itchat.load_login_status(pkl_dir):
                self.is_run = True
                info('Hotreload成功')
            else:
                self.logout()
                info('尚未成功登陆')
        else:
            self.is_run = True
