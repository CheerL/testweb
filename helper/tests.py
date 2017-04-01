from . import helper, models
from .base import get_now_week, HELPER, EXCEPTIONS, info

def test():
    #pass
    user = models.Helper_user.objects.filter(nick_name="步书宇")
    if user:
        return user[0]
    else:
        info('尚未绑定')
    print(user)
    # HELPER.show_remind_list(user.wx_UserName, user.nick_name)
