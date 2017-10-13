# -*- coding: utf-8 -*-
from flask_script import Manager
from flask import Flask, render_template
from flask_mail import Mail, Message
from threading import Thread
from mmysql import MysqlBase
import time

# from config import *

app = Flask(__name__)
app.config['MAIL_SERVER'] = "smtp.exmail.qq.com"
app.config['MAIL_PORT'] = '25'
# app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "whaley_alert@whaley.cn"
app.config['MAIL_PASSWORD'] = "7B8p2uFn"

mail = Mail(app)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def get_data_mysql(sql):
    conn_data = dict()
    conn_data['db'] = "bi"
    conn_data['host'] = "172.16.17.174"
    conn_data['user'] = "miles"
    conn_data['pswd'] = "aspect"

    m = MysqlBase(**conn_data)
    data = m.query(sql)
    return data


def return_yesterday(interval=3):
    base_time = time.time()
    before = base_time - interval * 24 * 3600
    return time.strftime("%Y%m%d", time.localtime(before))


@app.route('/send-mail/')
def index():
    days = return_yesterday()
    sql = "select day,host,sid,title,round(total_bytes/(1024*1024*1024),2),round(ratio*100,2),rank from cdn_sendbytes_statistics where rank<=10 and day='%s';" % days
    data = get_data_mysql(sql)
    msg = Message('主题', sender="whaley_alert@whaley.cn", recipients=["peng.tao@whaley.cn"])
    msg.subject = "%s高升CDN节目数据" % days
    msg.html = render_template('2.html', data=data, days=days)
    # with app.open_resource("1.png") as fp:
    #     msg.attach("image.png", "image/png", fp.read())

    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()

    return '<h1>邮件发送成功</h1>'


if __name__ == '__main__':
    app.run(debug=True)
