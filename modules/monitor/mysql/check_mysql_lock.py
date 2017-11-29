# -*- coding: utf-8 -*-
import logging
import commands
import json
import requests
import socket
import re
import sys

SEND_TO = "peng.tao@whaley.cn,lian.kai@whaley.cn"


def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = logging.getLogger()
    logname = sys.argv[0] + '.log'
    hdlr = logging.FileHandler(logname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)


def send_alter_mail(sub, body):
    mail_content = dict()
    mail_content["sub"] = sub
    mail_content["content"] = body
    mail_content["sendto"] = SEND_TO
    mail_url = 'http://10.19.15.127:5006/mail/api/v1.0/send'

    heads = {'content-type': 'application/json'}
    r = requests.post(url=mail_url, headers=heads, data=json.dumps(mail_content))
    if r.status_code == 200:
        log_msg("send_alter_mail", "send mail success", 1)
    else:
        err_msg = "send mail failed ,output was %s" % r.content
        log_msg("send_alter_mail", err_msg, 2)


def check_output(data):
    is_found = False
    for line in data.split('\n'):
        if len(line.split("|")) == 10:
            if re.search('lock', line.split("|")[7]) and int(line.split("|")[6]) > 300:
                is_found = True
                sub = "%s 出现mysql锁表，请人工介入" % socket.gethostname()
                body = "锁表相关信息如下：\n %s" % line
                send_alter_mail(sub, body)
    if is_found == False:
        msg = "check mysql no error"
        log_msg("check", msg, 1)
    else:
        log_msg("check", 'found block', 2)


def main():
    # check_cmd = "mysqladmin -uroot -p'aspect' processlist"
    check_cmd = "mysqladmin -uroot -p'moretvsmarTV@608_810' processlist"
    status, output = commands.getstatusoutput(check_cmd)
    if status == 0:
        check_output(data=output)
    else:
        msg = "Rum check cmd error,output was %s" % output
        log_msg("check_cmd", msg, 2)


if __name__ == "__main__":
    try:
        main()
    except:
        import StringIO, traceback

        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        # info = sys.exc_info()
        msg_errror = "mysql表锁检查脚本运行异常 %s" % message
        mail_sub = "%s mysql表锁检查脚本运行异常" % socket.gethostname()
        send_alter_mail(sub=mail_sub, body=msg_errror)
