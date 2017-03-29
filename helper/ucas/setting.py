'小助手设置'
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

    def __str__(self):
        return '\n'.join(
            ['%s:%s' % (self.trans_to_chinese(name), value) for name, value in vars(self).items()]
        )

    def trans_to_chinese(self, name):
        '转化为中文显示'
        return self.trans_dict[name]
