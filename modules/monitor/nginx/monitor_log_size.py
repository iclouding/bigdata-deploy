# -*- coding: utf-8 -*-
import logging
import os
import sys
import re
import json
import socket
import requests
import threading
import pdb

SENDTO = 'peng.tao@whaley.cn,lian.kai@whaley.cn'
CHECK_PATH = "/data/logs/nginx"


def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = logging.getLogger()
    logname = "%s.logs" % sys.argv[0]
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
    mysub = "Nginx_error_size_check %s " % socket.gethostname()
    mail_content["sub"] = mysub + sub
    mail_content["content"] = body
    mail_content["sendto"] = SENDTO
    mail_url = 'http://10.19.15.127:5006/mail/api/v1.0/send'

    heads = {'content-type': 'application/json'}
    r = requests.post(url=mail_url, headers=heads, data=json.dumps(mail_content))
    if r.status_code == 200:
        log_msg("send_alter_mail", "send mail success", 1)
    else:
        err_msg = "send mail failed ,output was %s" % r.content
        log_msg("send_alter_mail", err_msg, 2)


class CheckLogSzie():
    def __init__(self, filename, alter_size):
        self.filename = filename
        self.alter_size = alter_size

    def check(self):
        filesize = os.path.getsize(self.filename)
        if int(filesize) > int(self.alter_size):
            sub = "{0} 发现日志较大的文件 {1}".format(socket.gethostname(), self.filename)
            body = "{0} 文件大于设定值{2}，当前为{1}".format(self.filename, filesize,self.alter_size)
            log_msg("check", body, 2)
            send_alter_mail(sub, body)
            return False
        else:
            print "check {0} size {1} ".format(self.filename, filesize)
            return True


class GetFileByPath():
    """
    返回当前目录下匹配规则的文件名
    """

    def __init__(self, paths, pattern):
        self.paths = paths
        self.pattern = pattern

    def get_filename(self):
        files = list()
        for item in os.listdir(self.paths):
            full_name = os.path.join(self.paths, item)
            if os.path.isfile(full_name):
                if re.match(self.pattern, item):
                    files.append(full_name)
        return files


class MyThread(threading.Thread):
    def __init__(self, filename, alter_size):
        threading.Thread.__init__(self)
        self.filename = filename
        self.alter_size = alter_size

    def run(self):
        c = CheckLogSzie(self.filename, self.alter_size)
        c.check()


def main():
    pattern = "^sign_fail_.*.log$"
    alter_size = 1024 * 1024 * 1
    check_files = GetFileByPath(CHECK_PATH, pattern).get_filename()
    if not check_files:
        print "No files match"
    else:
        for check_file in check_files:
            t = MyThread(check_file, alter_size)
            t.start()


if __name__ == "__main__":
    try:
        main()
    except:
        import StringIO, traceback

        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        # info = sys.exc_info()
        msg_errror = "脚本运行异常 %s" % message
        mail_sub = "脚本运行异常"
        send_alter_mail(sub=mail_sub, body=msg_errror)
