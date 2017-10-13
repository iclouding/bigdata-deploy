#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
连凯需要的脚本，用于将HDFS上的目录逐个下载，打成tar包
'''

import os
import sys
import subprocess
import time


def initlog():
    import logging
    logger = None
    logger = logging.getLogger()
    logname="%s.log"%sys.argv[0]
    hdlr = logging.FileHandler(logname)
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


def read_files(filename):
    with open(filename, 'r') as f:
        data = f.read().strip()
    return data


def mkdir_(path):
    cmd_makedir = "mkdir -p %s" % path
    run_cmd(cmd_makedir)
    return True


def get_from_hdfs(path, base_dir):
    cmd = "cd %s && hadoop fs -get %s" % (base_dir, path)
    if run_cmd(cmd):
        return True
    else:
        return False


def get_path_list(path):
    path_list = list()
    full_item = os.listdir(path)
    for item in full_item:
        check_item = "%s/%s" % (path, item)
        if os.path.isdir(check_item):
            path_list.append(check_item)
    return path_list


def create_comp(path):
    path_list = get_path_list(path)
    for item in path_list:
        path_name = item.split("/")[-1]
        cmd = "cd %s && tar cvf %s.tar %s" % (path, path_name, path_name)
        run_cmd(cmd)

    return True


def get_date():
    now = time.strftime("%Y%m%d", time.localtime())
    return now


def main():
    base_dir = "/data1/hdfs_bak"
    now = get_date()
    work_dir = "%s/%s" % (base_dir, now)
    mkdir_(work_dir)
    config = sys.argv[1]
    filename = os.path.join(os.path.abspath('.'), config)
    target_dir = read_files(filename)
    for single_path in target_dir.split('\n'):
        get_from_hdfs(single_path, work_dir)
    create_comp(work_dir)


if __name__ == "__main__":
    main()
