#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
date: 2016/07/12
role: 发送邮件
usage: m = mailBase(log_path,mail_host='xxx',mail_user='xxx',mail_pswd='xxx',mail_send='xxx',mail_rece='xxx@xx.cn,xxx@xx.cn'])    实例化
       m.sendMail(subject, content, subtype='plain',charset='utf-8',['/data/a.txt','/data/b.txt'])
'''

from common import logMsg

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import sys


###mail操作类
class mailBase:
    def __init__(self, **args):

        ###获取参数
        self.host = args.get('mail_host')
        self.user = args.get('mail_user')
        self.pswd = args.get('mail_pswd')
        self.send = args.get('mail_send', 'whaley_alert@whaley.cn')
        self.rece = args.get('mail_rece', 'peng.tao@whaley.cn')

        ###收件人转成列表
        self._rece = self.rece.split(',')

        ###连接
        try:
            server = smtplib.SMTP()
            server.connect(self.host)
            ###选择是否基于ssl
            try:
                server.login(self.user, self.pswd)
            except:
                server.starttls()
                server.login(self.user, self.pswd)
            ###内部变量
            self._server = server
        except smtplib.SMTPException:
            logMsg('error', '%s connect error' % self.host, 2)
            raise ValueError('115,%s connect error %s' % self.host)

    ###析构函数 
    def __del__(self):
        self._server.quit()
        self._server.close()

    ###发送文件或html邮件    
    def sendMail(self, subject, content, subtype='plain', charset='utf-8', *attachs):
        if attachs:
            ###创建一个带附件的实例
            msg = MIMEMultipart()

            ###邮件正文内容
            msg.attach(MIMEText(content, subtype, charset))
        else:
            ###txt:plain  
            msg = MIMEText(content, subtype, charset)

            ###邮件标题
        msg['Subject'] = Header(subject, charset)

        ###附件
        for attach in attachs:
            ###判读文件是否存在
            if not os.path.isfile(attach):
                logMsg('error', '%s not exists' % attach, 2)
                raise ValueError('115,%s not exists' % attach)

            ###构造附件
            att = MIMEText(open(attach, 'rb').read(), 'base64', 'utf-8')
            att["Content-Type"] = 'application/octet-stream'

            ###分解附件路径中的文件名
            file_name = os.path.basename(attach)

            ###邮件中显示什么名字
            att["Content-Disposition"] = 'attachment; filename="%s"' % file_name
            msg.attach(att)

        ###添加发件人和收件人的显示
        msg['From'] = self.send
        msg['To'] = ";".join(self._rece)

        ###发送邮件
        try:
            self._server.sendmail(self.send, self._rece, msg.as_string())
            return True
        except Exception, e:
            logMsg('error', str(e), 2)
            return False


if __name__ == "__main__":
    mail_dict = dict()
    mail_dict['mail_host'] = "smtp.exmail.qq.com"  # 设置服务器
    mail_dict['mail_user'] = "whaley_alert@whaley.cn"  # 用户名
    mail_dict['mail_pswd'] = "7B8p2uFn"  # 口令
    mail_dict['mail_rece'] = sys.argv[1]

    m = mailBase(**mail_dict)
    sub = sys.argv[2]
    content = sys.argv[3]
    # attachs = '/tmp/miss_file.log'.split(',')
    # m.sendMail(sub, content, 'plain', 'utf-8', *attachs)
    m.sendMail(sub, content, 'plain', 'utf-8')
