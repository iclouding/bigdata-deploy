# -*- coding: utf-8 -*-


import commands
import json
import logging
import re
import sys
import socket
import requests
import config
import time
import threading
import psutil
import os


def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = logging.getLogger()
    logname = sys.argv[0] + '.logs'
    hdlr = logging.FileHandler(logname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)


def send_alter_mail(sub, body, sendto):
    mail_content = dict()
    mysub = " %s " % socket.gethostname()
    mail_content["sub"] = mysub + sub
    mail_content["content"] = body
    mail_content["sendto"] = sendto
    mail_url = 'http://10.19.15.127:5006/mail/api/v1.0/send'

    heads = {'content-type': 'application/json'}
    r = requests.post(url=mail_url, headers=heads,
                      data=json.dumps(mail_content))
    if r.status_code == 200:
        log_msg("send_alter_mail", "send mail success", 1)
    else:
        err_msg = "send mail failed ,output was %s" % r.content
        log_msg("send_alter_mail", err_msg, 2)


def run_command_out(cmd):
    status, out = commands.getstatusoutput(cmd)
    if status == 0:
        return out
    else:
        msg = "run cmd {0} Failed,output was {1} ".format(cmd, out)
        log_msg("run", msg, 2)
        return None
        # raise Exception(msg, 2)


class Checktask():
    def __init__(self, data):
        self.hosts = data['hosts']
        self.type = data['type']
        self.keyword = data['keyword']
        self.users = data['users']
        self.commands = data['commands']
        self.alter_mail = data['alter_mail']

    def check_workflow(self):
        #    check hostname match
        hostname = socket.gethostname()
        if hostname != self.hosts:
            return True
        if self.type == 'yarn_list':
            self.check_yarn_list_workflow()
        elif self.type == 'pid':
            self.check_ps_keyword_workflow()
        else:
            msg = "检查类型不是预定义的值"
            log_msg('check', msg, 2)
            raise Exception(msg, 2)

    def check_yarn_list_workflow(self):
        log_msg("check_yarn", "keyword %s,type %s" %
                (self.keyword, self.type), 1)
        if not self.check_yarn_service():
            start_service = "su - {0} -c '{1}'".format(
                self.users, self.commands)
            sub = "{0} {1} 服务不存在".format(socket.gethostname(), self.keyword)
            found_no_service = "{0} 服务并不存在，启动脚本开启服务".format(self.keyword)
            log_msg("check", found_no_service, 2)
            send_alter_mail(sub, found_no_service, self.alter_mail)
            run_command_out(start_service)
            time.sleep(60)
            if not self.check_yarn_service():
                sub = "{0} {1}服务重启未成功".format(
                    socket.gethostname(), self.keyword)
                start_failed = "{0}服务运行脚本开启服务失败".format(self.keyword)
                log_msg("start", start_failed, 2)
                send_alter_mail(sub, start_failed, self.alter_mail)
        log_msg("check_end", "check %s success!" % self.keyword, 1)

        # run command
        # check keyword

        # run commands

    def check_yarn_service(self):
        check_cmd = "su - {0} -c ' yarn application -list | grep {1}'".format(
            self.users, self.keyword)
        output = run_command_out(check_cmd)
        if output:
            check_item = output.split('\n')[-1].split()
            pattern = '^{0}$'.format(self.keyword)
            match = re.match(pattern, check_item[1])
            if match and check_item[5] == 'RUNNING':
                return True
            else:
                return False
        else:
            return False

    def check_ps_keyword_workflow(self):
        log_msg("check_ps", "keyword %s,type %s " %
                (self.keyword, self.type), 1)
        if not self.check_ps_keyword_service():
            start_service = "su - {0} -c '{1}'".format(
                self.users, self.commands)
            sub = "{0} {1} 服务不存在".format(socket.gethostname(), self.keyword)
            found_no_service = "{0} 服务并不存在，启动脚本开启服务".format(self.keyword)
            log_msg("check", found_no_service, 2)
            send_alter_mail(sub, found_no_service, self.alter_mail)
            os.system(start_service)
            # run_command_out(start_service)
            time.sleep(60)
            if not self.check_ps_keyword_service():
                sub = "{0} {1}服务重启未成功".format(
                    socket.gethostname(), self.keyword)
                start_failed = "{0}服务运行脚本开启服务失败".format(self.keyword)
                log_msg("start", start_failed, 2)
                send_alter_mail(sub, start_failed, self.alter_mail)
        log_msg("check_end", "check %s success!" % self.keyword, 1)

    def check_ps_keyword_service(self):
        pid = self.read_pid()
        is_found = False
        if pid:
            for proc in psutil.process_iter():
                try:
                    if int(proc.pid) == int(pid):
                        is_found = True
                except psutil.NoSuchProcess:
                    pass
            return is_found
        else:
            return is_found

    def read_pid(self):
        filename = '/tmp/%s.pid' % self.keyword
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                data = f.readline().strip()
            return data
        else:
            return None


class myThread(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data

    def run(self):
        c = Checktask(self.data)
        c.check_workflow()


def main():
    check_data = config.streaming
    for item in check_data:
        c = Checktask(item)
        c.check_workflow()
        del c
        # t = myThread(item)
        # t.start()


if __name__ == "__main__":
    main()
