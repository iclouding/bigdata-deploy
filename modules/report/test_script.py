# -*- coding: utf-8 -*-
from flask_script import Manager
from flask import Flask, render_template
from flask_mail import Mail, Message
from threading import Thread
from mmysql import MysqlBase
import time
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib

# from config import *

app = Flask(__name__)
app.config['MAIL_SERVER'] = "smtp.exmail.qq.com"
app.config['MAIL_PORT'] = '25'
# app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "whaley_alert@whaley.cn"
app.config['MAIL_PASSWORD'] = "7B8p2uFn"

mail = Mail(app)


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


class SendMail():
    def __init__(self, mailto='peng.tao@whaley.cn', subject='test'):
        self.subject = subject
        self.mailto = mailto

    def send_mail(self):
        msg = MIMEMultipart('related')
        emailfrom = "peng.tao@whaley.cn"
        msg['From'] = emailfrom
        msg['To'] = self.mailto
        msg['Subject'] = Header(self.subject, 'utf-8')
        days = return_yesterday()
        sql = "select day,host,sid,title,round(total_bytes/(1024*1024*1024),2),round(ratio*100,2),rank from cdn_sendbytes_statistics where rank<=10 and day='%s';" % days
        data = get_data_mysql(sql)
        mail_host = "smtp.exmail.qq.com"  # 设置服务器
        mail_user = "peng.tao@whaley.cn"  # 用户名
        mail_pass = "tel7206324"  # 口令
        body = render_template('2.html', data=data, days=days)
        msgText = MIMEText(body, 'html', 'utf-8')
        msg.attach(msgText)
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(emailfrom, self.mailto.split(","), msg.as_string())
            print "邮件发送成功"
        except smtplib.SMTPException:
            print "Error: 无法发送邮件"

        raise ("Get values error")


if __name__ == '__main__':
    mail = SendMail()
    mail.send_mail()
