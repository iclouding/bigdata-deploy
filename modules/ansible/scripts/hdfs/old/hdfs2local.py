#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
from optparse import OptionParser
import pdb


def initlog():
    import logging
    logger = None
    logger = logging.getLogger()
    hdlr = logging.FileHandler("hdfs2local.log")
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


def create_dir(dir_name):
    cmd = "mkdir -p %s" % dir_name
    run_cmd(cmd)
    return True


def get_hdfs2dir(hdfs, local):
    cmd = "hadoop fs -get %s/* %s/ " % (hdfs, local)
    run_cmd(cmd)
    return True


def read_files(filename):
    with open(filename, 'r') as f:
        data = f.read().strip()
    return data


def _rm_path(path):
    if path == "/":
        return False
    cmd1 = "rm -f %s/*" % path
    run_cmd(cmd1)
    cmd2 = "rmdir %s " % path
    run_cmd(cmd2)
    return True


def main():
    config = sys.argv[1]
    filename = os.path.join(os.path.abspath('.'), config)
    check_dir = read_files(filename)
    dir_suffer = '/data'
    for dir_ in check_dir.split('\n'):
        if dir_:
            dir_local = dir_suffer + dir_
            _rm_path(dir_local)
            msg = "Starting copying %s" % dir_
            logMsg("copy", msg, 1)
            create_dir(dir_local)
            get_hdfs2dir(dir_, dir_local)


if __name__ == "__main__":
    main()
