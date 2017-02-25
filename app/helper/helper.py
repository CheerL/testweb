# _*_ coding: utf-8 _*_
'小助手'
import os
import re
import time
import datetime
import requests
import itchat
import pandas as pd
from app.helper.wheel import parallel as pl
from .ucas import _info, UCASSEP, EXCEPTIONS

TL_KEY = '71f28bf79c820df10d39b4074345ef8c'
SAVE_TIME = 1#分钟
REMIND_BEFORE = 30#分钟
REMIND_WAIT = 5#分钟
A_WEEK = 60 * 60 * 24 * 7#秒
END_WEEK = 20
FILE_NAME = 'data.csv'
WEEK = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
WEEK_DICT = dict(map(lambda x, y: [x, y], WEEK, [i for i in range(7)]))
COURSE_NUM = [str(i) for i in range(1, 12)]
COURSE_DICT = dict(map(lambda x, y: [x, y], COURSE_NUM, (
    [8, 30], [9, 20], [10, 30], [11, 20],
    [13, 30], [14, 20], [15, 30], [16, 20],
    [19, 00], [20, 00], [21, 00]
    )))

class Helper(object):
    '助手类'
    user_list = None
    remind_alive = True
    friends = None
    admin = None

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
    def _show_remind_list(nick_name, remind_list):
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
        msg = _info(error)
        print(msg)
        if not up_rep:
            Helper.send(msg, user)
        else:
            raise NotImplementedError(error)

    @staticmethod
    def send(msg, user=None):
        '搜索用户并发送, 默认发给自己'
        try:
            if user:
                if isinstance(user, dict):
                    if 'UserName' in user.keys():
                        user_name = user['UserName']
                    elif 'nick_name' in user.keys():
                        _user = itchat.search_friends(nickName=user['nick_name'])[0]
                        user_name = _user['UserName']
                elif isinstance(user, str):
                    if '@' in user:
                        user_name = user
                    else:
                        _user = itchat.search_friends(name=user)[0]
                        user_name = _user['UserName']
                else:
                    user_name = None
            else:
                user_name = None
            itchat.send(msg, user_name)
        except EXCEPTIONS as error:
            print(error)
            itchat.send(msg)

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
        except:
            # 将会返回一个None
            return

    def __init__(self):
        '初始化'
        if os.path.isfile(FILE_NAME) and os.path.getsize(FILE_NAME) > 100:
            temp = pd.read_csv(FILE_NAME).fillna(value=False).T
            def _get_course_list(item):
                if not 'course_list' in item.keys():
                    return
                if item['course_list']:
                    temp_list = re.findall(r'{(.*?)}', item['course_list'])
                    weeks = [re.findall(r"'weeks': \('(.*?)', '(.*?)'\)", a)[0] for a in temp_list]
                    _times = [re.findall(r"'times': \[(\(.*?\))\]", a)[0].split(r'), ')
                              for a in temp_list]
                    times = [[(re.findall(r"'(星期.)'", x)[0], tuple(re.findall(r"'(\d*?)'", x)))
                              for x in a] for a in _times]
                    name = [re.findall(r"'{}': '(.*?)'".format('name'), a)[0] for a in temp_list]
                    num = [re.findall(r"'{}': '(.*?)'".format('num'), a)[0] for a in temp_list]
                    place = [re.findall(r"'{}': '(.*?)'".format('place'), a)[0] for a in temp_list]
                    return [dict(num=num[i],
                                 place=place[i],
                                 weeks=weeks[i],
                                 times=times[i],
                                 name=name[i]) for i in range(len(temp_list))]

            def _get_remind_list(item):
                if not 'remind_list' in item.keys():
                    return
                if item['remind_list']:
                    return [(each[0], each[1], float(each[2]))
                            for each in re.findall(
                                r"\('(.*?)', '(.*?)', (.*?)\)", item['remind_list']
                                )]

            for i in temp:
                item = temp[i]
                item['course_list'] = _get_course_list(item)
                item['remind_list'] = _get_remind_list(item)

            self.user_list = [temp[num].to_dict() for num in temp]
        else:
            self.user_list = list()

    def search_list(self, nick_name, is_rep=True, is_index=False):
        '在用户列表中查找当前用户是否已经绑定'
        for index, user in enumerate(self.user_list):
            if user['nick_name'] == nick_name:
                if is_index:
                    return index
                else:
                    return user
        if is_rep:
            raise NotImplementedError('尚未绑定')
        else:
            return None

    def update_info(self, user=None):
        '更新用户信息'
        if user:
            try:
                sep = UCASSEP(user)
                sep.get_course_list()
                user['user_name'] = sep.user_name
                user['course_list'] = sep.course_list
            except EXCEPTIONS as error:
                self.my_error(error, user)
        else:
            for user in self.user_list:
                self.update_info(user)

    def add_user(self, now_user, nick_name, text):
        '新增提醒用户'
        user = self.search_list(nick_name, is_rep=False)
        if user:
            self.send('你已经绑定过啦', now_user)
        else:
            try:
                result = re.findall(r'用户名[:：\s]*(.+?)\s*密码[:：\s]*(.+?)$', text)
                if result:
                    user_id = result[0][0]
                    password = result[0][1]
                else:
                    raise IOError('输入格式错误, 请输入"绑定 用户名:***  密码:***"')
                user = dict(
                    nick_name=nick_name,
                    user_id=user_id,
                    password=password,
                    is_open=True,
                    have_remind=False
                    )
                self.update_info(user)
                self.user_list.append(user)
                self.send('绑定成功', now_user)
            except EXCEPTIONS as error:
                self.my_error(error, now_user)

    def change_user(self, now_user, nick_name, text):
        '修改用户信息'
        try:
            user = self.search_list(nick_name)
            if '用户名' in text:
                user_ids = re.findall(r'用户名[:：\s]*(.*?)(\s*|\s+\S*\s*?)$', text)
                if user_ids:
                    user['user_id'] = user_ids[0][0]
                else:
                    raise IOError('输入格式错误, 请输入"绑定 用户名:***"')
            if '密码' in text:
                passwords = re.findall(r'密码[:：\s]*(.*?)(\s*|\s+\S*\s*?)$', text)
                if passwords:
                    user['password'] = passwords[0][0]
                else:
                    raise IOError('输入格式错误, 请输入"绑定 密码:***"')
            self.update_info(user)
            self.send('修改绑定信息成功', now_user)
        except EXCEPTIONS as error:
            self.my_error(error, now_user)

    def del_user(self, now_user, nick_name):
        '删除用户'
        try:
            index = self.search_list(nick_name, is_index=True)
            self.user_list.pop(index)
            self.send('取消绑定成功', now_user)
        except EXCEPTIONS as error:
            self.my_error(error, now_user)

    def cancel_remind(self, now_user, nick_name):
        '取消提醒'
        try:
            user = self.search_list(nick_name)
            user['is_open'] = False
            self.send('取消提醒成功', now_user)
        except EXCEPTIONS as error:
            self.my_error(error)

    def save_user_list(self, now_user=None):
        '保存用户信息为csv'
        data = pd.DataFrame(self.user_list)
        data.to_csv(FILE_NAME, encoding='utf-8', index=False)
        self.send('保存成功', now_user)

    def auto_save(self):
        '每间隔一段时间自动保存一次'
        sleep_time = SAVE_TIME*60#秒
        def _auto_save():
            while True:
                self.save_user_list()
                time.sleep(int(sleep_time))

        if not pl.search_thread('auto_save'):
            pl.run_thread([(_auto_save, ())], name='auto_save', is_lock=False)

    def remind(self, now_user=None, nick_name=None):
        '定时提醒'
        def _remind_do(remind, user):
            _time = time.strftime('%H:%M', time.localtime(remind[2]))
            msg = '今天{}在{}上{}, 不要迟到哦'.format(_time, remind[1], remind[0])
            print(msg)
            self.send(msg, user)

        def _remind_main(user):
            if user['is_open']:
                nick_name = user['nick_name']
                if 'remind_list' not in user.keys() or not user['remind_list']:
                    self. __remind_list_update(user)
                try:
                    remind_list = user['remind_list']
                    result = self._show_remind_list(nick_name, remind_list)
                    if result[1] > 0:                               #当上课时间到, 把课程清理出提醒队列
                        remind_list.pop(0)
                        self.__remind_list_update(user)
                    elif result[1] + REMIND_BEFORE * 60 >= 0:       #当提醒时间到, 主动提醒一次
                        if not user['have_remind']:                 #当没有提醒过
                            _remind_do(remind_list[0], user)        #提醒
                            user['have_remind'] = True              #修改为已经提醒过
                    else:                                           #没有到提醒时间
                        user['have_remind'] = False
                except EXCEPTIONS as error:
                    self.my_error(error, user)

        def _remind():
            while self.remind_alive:
                for user in self.user_list:
                    if user['is_open']:
                        _remind_main(user)
                time.sleep(int(REMIND_WAIT * 60))

        if self.get_now_week() > END_WEEK:
            self.remind_alive = False
            raise NotImplementedError('学期已经结束')
        if nick_name:
            user = self.search_list(nick_name)
            user['is_open'] = True
            self.send('打开提醒成功', now_user)
        else:
            try:
                pl.run_thread([(_remind, ())], 'remind', False)
            except EXCEPTIONS as error:
                self.my_error(error)

    def __remind_list_update(self, user):
        '更新提醒列表'
        def _remind_list_update_main(week, course_list, count=0):
            if week + count > END_WEEK:
                user['is_open'] = False
                raise NotImplementedError('%s本学期已经没有课了' % (user['nick_name']))
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
                user['remind_list'] = remind_list
            else:
                return _remind_list_update_main(week, course_list, count + 1)

        self.update_info(user)
        course_list = user['course_list']
        week = self.get_now_week()
        _remind_list_update_main(week, course_list)

    def remind_list_update(self, now_user, nick_name):
        '手动更新信息'
        try:
            user = self.search_list(nick_name)
            self.__remind_list_update(user)
            self.send('信息更新成功', now_user)
        except EXCEPTIONS as error:
            self.my_error(error)

    def help(self, now_user, keys):
        '显示帮助'
        msg = '功能有: ' + ', '.join([', '.join(each) for each in keys])
        self.send(msg, now_user)
        self.send('相信你看名字就会用了', now_user)

    def show_course_list(self, now_user, nick_name, is_pic=True, is_with_num=False):
        '显示课表'
        try:
            user = self.search_list(nick_name)
            if is_pic:
                try:
                    pic_name = 'pic\\' + user['nick_name'] + '-course.png'
                    self.send('正在获取课表, 这可能会花上10秒到30秒', now_user)
                    UCASSEP(user).get_course_list_pic(pic_name)
                    self.send('@img@' + pic_name, now_user)
                except EXCEPTIONS as error:
                    if os.path.isfile(pic_name):
                        self.send('@img@' + pic_name, now_user)
                        self.send('更新课表出错, 返回旧课表')
                    self.my_error(error, now_user)
            else:
                course_list = user['course_list']
                _course_list = list()
                for course in course_list:
                    place = course['place']
                    name = course['name']
                    nob = course['num']
                    _course_list += [(name, place, day, num, nob) for (day, num) in course['times']]
                _course_list.sort(key=lambda x: self.get_course_time(x[2], x[3][0]))
                if not is_with_num:
                    msg = '\n'.join(['{}, {}, {}, 第{}节'.format(
                        course[0], course[1], course[2],
                        '.'.join(course[3])) for course in _course_list])
                else:
                    msg = '\n'.join(['{}, {}, {}, 第{}节, 编号{}'.format(
                        course[0], course[1], course[2],
                        '.'.join(course[3]), course[4]) for course in _course_list])
                self.send(msg, now_user)
        except EXCEPTIONS as error:
            self.my_error(error, now_user)

    def show_remind_list(self, now_user, nick_name):
        '显示提醒时间'
        try:
            user = self.search_list(nick_name)
            remind_list = user['remind_list']
            result = self._show_remind_list(nick_name, remind_list)
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
                raise IOError('输入格式错误, 应为"选课 编号:***"')
            sep = UCASSEP(user)
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
                raise IOError('输入格式错误, 应为"选课 编号:***"')
            sep = UCASSEP(user)
            sep.get_course_list()
            if sep.drop_course(num):
                self.send('退课成功', now_user)
            else:
                self.send('退课失败', now_user)
        except EXCEPTIONS as error:
            self.my_error(error)

if __name__ is '__main__':
    import main
    main.main()