# -*- coding: utf-8 -*-
import commands
import sys
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

base = 500
warn = 800


def logMsg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = None
    logger = logging.getLogger()
    logname = sys.argv[0] + '.log'
    hdlr = logging.FileHandler(logname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)  # 网络上的实现基本为说明这条语句的使用和作用


class mailBase:
    def __init__(self, **args):

        ###获取参数
        self.host = args.get('mail_host')
        self.user = args.get('mail_user')
        self.pswd = args.get('mail_pswd')
        self.send = args.get('mail_send', 'peng.tao@whaley.cn')
        self.rece = args.get('mail_rece', 'pt_yc@163.com')

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


def get_top_values():
    cmd = "top |head -n 12"
    out = commands.getoutput(cmd)
    data = out.split('\n')[-5:]
    return data


def main():
    data = get_top_values()
    logMsg("start", "check Start!", 1)
    for item in data:
        if float(item.split()[9]) > float(base):
            msg = "process CPU is High,values  %s" % str(item.split()[9])
            logMsg("check_cpu", msg, 2)
            pid = item.split()[1]
            process_cmd = "ps -ef|grep %s |grep -Ev grep" % pid
            data = commands.getoutput(process_cmd)
            process_msg = "Process info: %s" % data
            logMsg("check_cpu", process_msg, 2)

        if float(item.split()[9]) > float(warn):
            mail_dict = dict()
            mail_dict['mail_host'] = "smtp.exmail.qq.com"  # 设置服务器
            mail_dict['mail_user'] = "peng.tao@whaley.cn"  # 用户名
            mail_dict['mail_pswd'] = "tel7206324"  # 口令
            mail_dict['mail_rece'] = 'peng.tao@whaley.cn,lian.kai@whaley.cn,wang.baozhi@whaley.cn'  # 发送给
            m = mailBase(**mail_dict)
            import socket
            hostname = socket.gethostname()
            sub = "%s CPU 过高报警" % hostname
            content = "%s \n %s" % (msg, process_msg)
            m.sendMail(sub, content, 'plain', 'utf-8')


if __name__ == "__main__":
    main()
