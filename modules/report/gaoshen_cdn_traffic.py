# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_mail import Mail, Message
from threading import Thread
from mmysql import MysqlBase
import time

app = Flask(__name__)
app.config['MAIL_SERVER'] = "smtp.exmail.qq.com"
app.config['MAIL_PORT'] = '25'
app.config['MAIL_USERNAME'] = "whaley_alert@whaley.cn"
app.config['MAIL_PASSWORD'] = "7B8p2uFn"

mail = Mail(app)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def get_data_mysql(conn, sql):
    m = MysqlBase(**conn)
    data = m.query(sql)
    return data


def return_yesterday(interval=1):
    base_time = time.time()
    before = base_time - interval * 24 * 3600
    return time.strftime("%Y%m%d", time.localtime(before))


@app.route('/send-gaoshen-mail/')
def index():
    days = return_yesterday()
    sql_moguv = "select day,host,sid,title,round(ratio*100,2),rank from cdn_sendbytes_statistics where rank<=10 and host='mediags.moguv.com' and day='%s';" % days
    sql_moguv_2 = "select day,host,sid,title,round(ratio*100,2),rank from cdn_sendbytes_statistics where rank<=10 and host='mediags2.moguv.com' and day='%s';" % days
    sql_moretv = "select day,host,sid,title,round(ratio*100,2),rank from cdn_sendbytes_statistics where rank<=10 and host='mediags.moretv.com.cn' and day='%s';" % days

    conn_data = dict()
    conn_data['db'] = "bi"
    conn_data['host'] = "10.19.72.224"
    conn_data['user'] = "bi"
    conn_data['pswd'] = "mlw321@moretv"

    data_moguv = get_data_mysql(conn_data, sql_moguv)
    data_moguv_2 = get_data_mysql(conn_data, sql_moguv_2)
    data_moretv = get_data_mysql(conn_data, sql_moretv)
    #if data_moguv and data_moretv and data_moguv_2 :
    if data_moguv and data_moguv_2 :
        msg = Message('主题', sender="whaley_alert@whaley.cn",
                      recipients=["peng.tao@whaley.cn", "zhang.qiangjun@whaley.cn", "wu.qi@whaley.cn",
                                  "wu.qiang@whaley.cn", "ge.yongliang@whaley.cn"]
                      # recipients=["peng.tao@whaley.cn"]
                      )
        msg.subject = "%s高升CDN节目数据" % days
        msg.html = render_template('gaoshen_cdn_traffic.html', data_moguv=data_moguv, data_moguv_2=data_moguv_2,
                                   data_moretv=data_moretv, days=days)
    else:
        msg = Message('主题', sender="whaley_alert@whaley.cn",
                      recipients=["peng.tao@whaley.cn", "zhang.qiangjun@whaley.cn", "feng.jin@whaley.cn","lian.kai@whaley.cn", "ge.yongliang@whaley.cn"]
                      # recipients=["peng.tao@whaley.cn"]
                      )
        msg.subject = "%s高升CDN节目数据异常报警" % days
        msg.html = render_template('gaoshen_cdn_traffic_error.html', data_moguv=data_moguv, data_moguv_2=data_moguv_2,data_moretv=data_moretv,days=days)
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()

    return '<h1>邮件发送成功</h1>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
