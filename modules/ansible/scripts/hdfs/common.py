#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
通用日志，执行命令方法，读取配置文件，读写文件等
'''

import sys
import subprocess
import time


def logMsg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    import logging
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


def read_files(filename):
    with open(filename, 'r') as f:
        data = f.read().strip()
    return data


def run_cmd(cmd):
    msg = "Starting run: %s " % cmd
    logMsg("run_cmd", msg, 1)
    cmdref = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error_info = cmdref.communicate()
    if error_info:
        if isinstance(error_info, list) or isinstance(error_info, tuple):
            error_info = error_info[0]
        msg = "RUN %s ERROR,error info:  %s" % (cmd, error_info)
        logMsg("run_cmd", msg, 2)
        return False
    else:
        # print "Run Success!!"
        return output


def write_file(filename, data):
    with open(filename, 'a+') as f:
        f.write(data)
        f.write('\n')
    return True


def return_day(num):
    now = time.time()
    before = now - num * 24 * 3600
    return time.strftime("%Y%m%d", time.localtime(before))


def get_date():
    now = time.strftime("%Y%m%d", time.localtime())
    return now

