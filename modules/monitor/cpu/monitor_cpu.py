# -*- coding: utf-8 -*-
import commands
import sys
import logging
import os
import requests
import socket
import time
import json


base = 500
warn = 800
SEND_TO='peng.tao@whaley.cn,lian.kai@whaley.cn,wang.baozhi@whaley.cn' 

def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = None
    logger = logging.getLogger()
    # logname = sys.argv[0] + '.log'
    logname = "/data/logs/systemInfo/monitor_cpu.log"
    hdlr = logging.FileHandler(logname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)  # 网络上的实现基本为说明这条语句的使用和作用


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

def get_top_values():
    cmd = "top |head -n 12"
    out = commands.getoutput(cmd)
    data = out.split('\n')[-5:]
    return data


def write_process_info():
    baseFilename = "/data/logs/systemInfo/processInfo"
    filename = "%s_%s.log" % (baseFilename, time.strftime("%Y%m%d%H%M%S", time.localtime()))
    cmd = "ps -ef > %s" % filename
    commands.getoutput(cmd)


def main():
    data = get_top_values()
    log_msg("check_cpu", "start check", 1)
    for item in data:
        if float(item.split()[9]) > float(base):
            msg = "process CPU is High,values  %s" % str(item.split()[9])
            log_msg("check_cpu", msg, 2)
            pid = item.split()[1]
            process_cmd = "ps -ef|grep %s |grep -Ev grep" % pid
            data = commands.getoutput(process_cmd)
            process_msg = "Process info: %s" % data
            log_msg("check_cpu", process_msg, 2)

            if float(item.split()[9]) > float(warn):
                hostname = socket.gethostname()
                sub = "%s CPU 过高报警" % hostname
                content = "%s \n %s" % (msg, process_msg)
                send_alter_mail(sub=sub, body=content)
                write_process_info()

    if __name__ == "__main__":
        main()