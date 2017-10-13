# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_mail import Mail
from flask_mail import Message


def send_mail(username, link):
    app = Flask(__name__)
    app.config.update(
        # DEBUG=True,
        # EMAIL SETTINGS
        MAIL_SERVER="smtp.exmail.qq.com",
        MAIL_PORT=25,
        MAIL_USERNAME="whaley_alert@whaley.cn",
        MAIL_PASSWORD="7B8p2uFn"
    )
    mail = Mail(app)
    try:
        msg = Message("Send Mail Tutorial!",
                      sender="whaley_alert@whaley.cn",
                      recipients=["pt_yc@163.com", "peng.tao@whaley.cn"])
        msg.body = "Yo!\nHave you heard the good word of Python???"
        #msg.body = 'Hello ' + username + ',\nYou or someone else has requested that a new password be generated for your account. If you made this request, then please follow this link:' + link
        #msg.html = render_template('1.html', username=username, link=link)
        # msg.rich = render_template('email.html', name=name)
        mail.send(msg)
        return 'Mail sent!'
    except Exception, e:
        return (str(e))


if __name__ == "__main__":
    send_mail('miles', 'http://163.com')

    # mail_dict['mail_host'] = "smtp.exmail.qq.com"  # 设置服务器
    # mail_dict['mail_user'] = "whaley_alert@whaley.cn"  # 用户名
    # mail_dict['mail_pswd'] = "7B8p2uFn"  # 口令
