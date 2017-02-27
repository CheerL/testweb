# _*_ coding: utf-8 _*_
'国科大教育系统选课程序'
import re
import time
from selenium import webdriver
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as Bs
from PIL import Image, ImageDraw, ImageFont
from .wheel import parallel as pl
from . import logger, EXCEPTIONS, WEEK, TIMEOUT

PHANTOMJS_PATH = 'static/phantomjs.exe'

def _info(msg):
    return '%s\n%s' % (time.ctime(), str(msg))

def _rep(msg):
    logger.info(msg)

def _error(error, is_up_rep=True):
    _rep(error)
    if is_up_rep:
        raise NotImplementedError(error)

class UCASSEP(object):
    'UCAS SEP系统'
    user_id = ''
    password = ''
    user_name = ''
    course_list = []
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
            _error(error)

    def _get_json(self, url, data=None, empty_post_tag=False):
        try:
            response = self._get(url, data, empty_post_tag)
            return response.json()
        except EXCEPTIONS:
            _error('该网页返回的不是json数据')

    def _get_page(self, url, data=None, empty_post_tag=False):
        try:
            response = self._get(url, data, empty_post_tag)
            return Bs(response.text, 'html.parser')
        except EXCEPTIONS:
            _error('无法解析该网页')

    def __init__(self, user):
        try:
            if isinstance(user, dict):
                self.session.headers.update({
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest',
                    })
                if user['user_id'] and user['password']:
                    self.user_id = user['user_id']
                    self.password = user['password']
                else:
                    raise KeyError('"user"中不存在用户名和密码')
                self.login()
                self.login_course()
            else:
                raise TypeError('"user"不是一个字典')
        except EXCEPTIONS as error:
            _error('用户信息错误, {}'.format(error))

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
                _rep('{}登陆成功'.format(self.user_name))
            else:
                raise NotImplementedError(result['msg'])
        except EXCEPTIONS as error:
            _error(error)

    def logout(self):
        '退出登陆'
        url = 'http://sep.ucas.ac.cn/logout?o=platform'
        self._get(url=url)
        self.is_login = False
        _rep('{}退出登陆'.format(self.user_name))

    def login_course(self):
        '登陆至选课系统'
        if self.is_login is False:
            _rep('尚未成功登陆SEP')
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
                    _rep('登陆SEP系统失效, 重新登陆')
                    self.login()

    def is_chosen(self, course):
        '查看该课程是否已经选上'
        if not isinstance(course, str):
            course = str(course)
        if not self.course_list:
            self.get_course_list()
        for item in self.course_list:
            if item['num'] == course:
                _rep('{}已经选上'.format(item['name']))
                result = True
                break
        else:
            _rep('编号为{}的课程未选上'.format(course))
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
                    _rep(soup.find('label', 'success').contents[0])
                    return True
                elif len(soup.find('label', 'error').contents) is not 0:
                    _rep(soup.find('label', 'error').contents[0])
                    return False
                else:
                    raise NotImplementedError('获取选课结果时出现异常错误')
            except EXCEPTIONS as error:
                _error(error)
                return False

    def drop_course(self, course):
        '退课'
        if self.is_chosen(course):
            url = 'http://jwxk.ucas.ac.cn/courseManageBachelor/del/' + course + '?s='
            try:
                soup = self._get_page(url)
                if len(soup.find('label', 'success').contents) is not 0:
                    _rep(soup.find('label', 'success').contents[0])
                    return True
                elif len(soup.find('label', 'error').contents) is not 0:
                    _rep(soup.find('label', 'error').contents[0])
                    return False
                else:
                    raise NotImplementedError('获取退课结果时出现异常错误')
            except EXCEPTIONS as error:
                _error(error)
                return True
        else:
            _rep('课程未选上, 无法退课')
            return False

    def get_all_list(self, num):
        '获取课程列表'
        base_url = 'http://jwxk.ucas.ac.cn/course/coursetime/'
        try:
            soup = self._get_page(base_url + str(num))
            title = str(soup.find('p').contents[0])
            pl.my_print('%s %s' % (num, title), 'temp.txt', 2)
        except EXCEPTIONS:
            pass

    def get_course_list(self):
        '获取已选择课程, 并储存'
        self.course_list.clear()
        url = 'http://jwxk.ucas.ac.cn/courseManageBachelor/main'
        soup = self._get_page(url)
        pattern = re.compile(r'/course/coursetime/(\d*)')
        for item in soup.find_all('a', href=pattern):
            num = re.findall(pattern, item['href'])[0]
            name = item.contents[0]
            link = 'http://jwxk.ucas.ac.cn/course/coursetime/' + num
            soup = self._get_page(link)
            weeks = soup.find_all('th', text='上课周次')[0]\
                .next_sibling.next_sibling.contents[0].split('、')
            weeks = (str(int(weeks[0]) - 1), str(int(weeks[-1]) - 1))
            place = soup.find_all('th', text='上课地点')[0].next_sibling.next_sibling.contents[0]
            times = [td.next_sibling.next_sibling.contents[0].replace('。', '').split('： ')\
                for td in soup.find_all('th', text='上课时间')]
            times = [(
                re.findall(re.compile(r'(星期.?)'), each[0])[0],
                tuple(re.findall(re.compile(r'(\d*)[、节]'), each[1]))
                ) for each in times]
            course = dict(num=num, name=name, weeks=weeks, place=place, times=times)
            self.course_list.append(course)
        _rep('课表获取成功')

    def get_course_list_pic(self, pic_name):
        '生成图片'
        def get_time_table(course_list):
            '转换课表为矩阵形式'
            table = np.zeros((7, 11)).astype(str)
            for index, day in enumerate(WEEK):
                for num in range(1, 12):
                    for course in course_list:
                        week = 1
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

        def draw_font(x, y, text, color=black, indent=0.5):
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
        black = (0, 0, 0)
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
        course_list = self.course_list
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

    def save_course_list(self):
        '保存课程列表'
        filename = '{}.csv'.format(self.user_name)
        pd.DataFrame(self.course_list).to_csv(filename, encoding='utf-8')
        _rep('课表已保存为{}'.format(filename))


def main():
    '主函数'
    try:
        userLCR = {
            'user_id':'1017801883@qq.com',
            'password':'lcr0717'
            }
        LCR = UCASSEP(userLCR)
        req = [(LCR.get_all_list, (num,)) for num in range(133000)]
        pl.run_thread_pool(req, is_lock=True, limit_num=30)
    except EXCEPTIONS as error:
        _error(error, False)

if __name__ == '__main__':
    main()
