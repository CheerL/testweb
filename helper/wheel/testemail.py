'造轮大法好 の 简易邮件发送模块'
import smtplib
import re
from email.mime.text import MIMEText
from email.header import Header

class Mail:
    ''' 邮件类:
        sender:             发件邮箱
        host:               发件邮箱smtp服务器地址
        reciever:           收件邮箱
        __password:         发件邮箱密码
        __result:           发件结果
        '''

    sender = ''
    reciever = ''
    host = ''
    __password = ''
    __result = False

    def __init__(self, sender, password, reciever, host):
        self.sender = sender
        self.__password = password
        self.reciever = reciever
        self.host = host

    def __str__(self):
        return '发件邮箱:' + self.sender + '\n收件邮箱:' + self.reciever + '\n发件邮箱smtp服务器地址:' + self.host

    def change_sender(self, new_sender):
        '修改发件邮箱'
        self.sender = new_sender

    def change_password(self, new_password):
        '修改发件邮箱密码'
        self.__password = new_password

    def change_reciever(self, new_reciever):
        '修改收件邮箱'
        self.reciever = new_reciever

    def chang_host(self, new_host):
        '修改smtp服务器地址'
        self.host = new_host

    def send(self, content, title, user_nickname='', re_nickname='', para='plain'):
        ''' 邮件发送函数
            return					True/False
            my_content				邮件正文
            my_title:				邮件标题
            user_nickname:			发件人昵称, 可选参数
            re_nickname:			收件人昵称, 可选参数
            para:					发件模式, 可选参数, 默认plain, 可修改为html
            '''
        if user_nickname == '':
            user_nickname = re.findall(r'^(.*?)@', self.sender)[0]
        if re_nickname == '':
            re_nickname = re.findall(r'^(.*?)@', self.reciever)[0]
        try:
            msg = MIMEText(content, para, 'utf-8')
            msg['From'] = user_nickname
            msg['to'] = re_nickname
            msg['Subject'] = Header(title, 'utf-8')

            server = smtplib.SMTP()  # 发件人邮箱中的SMTP服务器，端口是25
            server.connect(self.host, 25)
            server.login(self.sender, self.__password)
            server.sendmail(self.sender, self.reciever, msg.as_string())
            server.quit()  # 关闭连接
            self.__result = True
        except smtplib.SMTPException:  # 如果try中的语句没有执行，则会执行下面的ret=False
            self.__result = False

    def show_result(self):
        '返回发送结果'
        return self.__result

if __name__ == '__main__':
    '''
    # 示范
    SENDER = 'linchenran14@mails.ucas.ac.cn'
    PASSWD = 'lcr19960717'
    RECIEVER = '1017801883@qq.com'
    HOST = 'smtp.cstnet.cn'
    CONTENT = '你明天有事么?'
    TITLE = 'Hello'
    NICKNAME = 'Cheer.L'
    new_mail = Mail(SENDER, PASSWD, RECIEVER, HOST)
    new_mail.send(CONTENT, TITLE, NICKNAME, NICKNAME)
    print(new_mail.show_result())
    '''
