#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import subprocess
import os
import sys
import pdb
import socket
import re


def initlog():
    import logging
    logger = None
    logger = logging.getLogger()
    log_name = sys.argv[0].split(".")[0] + ".log"
    hdlr = logging.FileHandler(log_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return [logger, hdlr]


def logMsg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger, hdlr = initlog()
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)  # 网络上的实现基本为说明这条语句的使用和作用


def get_host():
    host_name = socket.gethostname()
    return host_name


def _run_cmd(cmd):
    print "Starting run: %s " % cmd
    cmdref = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out = cmdref.stdout.read()
    print "run cmd  output " + out
    data = cmdref.communicate()
    if cmdref.returncode == 0:
        msg = "Run %s success \n" % cmd
        msg = msg + data[0]
        print(msg)
        return True
    else:
        msg = "[ERROR] Run %s False \n" % cmd
        msg = msg + data[1]
        logMsg("Run", msg, 2)
        return False


def modi_hostname(host_name, filenames):
    cmd = "sed -i 's#%s#%s#g' %s" % ('{{hostname}}', host_name, filenames)
    print "Run_Cmd was : %s" % cmd
    _run_cmd(cmd)


def main():
    host_name = get_host()
    filenames = sys.argv[1]
    modi_hostname(host_name, filenames)


if __name__ == '__main__':
    main()
