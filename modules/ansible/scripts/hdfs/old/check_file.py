#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
按配置文件的目录信息生成本地&远程(HDFS)文件信息，将其写入local.txt及remote.txt文件中
'''
import subprocess
import commands
import sys
import os
import json
from optparse import OptionParser
import pdb


def initlog():
    import logging
    logger = None
    logger = logging.getLogger()
    hdlr = logging.FileHandler("hdfs_command.log")
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
    msg = commands.getoutput(cmd)
    return msg.strip()


def check_local_path(path):
    check_files = []
    return_local = dict()
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                check_files.append(os.path.join(root, file))
    for check_one in check_files:
        return_local[check_one[5:]] = _get_local_info(check_one)
    return return_local


def _get_local_info(filename):
    local_size = os.path.getsize(filename)
    return local_size


def read_files(filename):
    with open(filename, 'r') as f:
        data = f.read().strip()
    return data


def get_remote_size(path):
    return_dict = dict()
    cmd = "hadoop fs -ls -R %s" % path
    output = run_cmd(cmd).split('\n')
    for line in output:
        return_dict[line.split()[7]] = line.split()[4]
    return return_dict


def write_file(filename, data):
    context = ""
    for key_ in data.keys():
        line = "%s#@#%s\n" % (key_, str(data[key_]))
        context += line

    with open(filename, 'a+') as f:
        f.write(context)


def main():
    filename = os.path.join(os.path.abspath('.'), 'hdfs1.txt')
    check_dir = read_files(filename)
    pdb.set_trace()
    output_local_file = 'local.log'
    output_remote_file = 'remote.log'
    for dir_ in check_dir.split('\n'):
        if dir_:
            remote = get_remote_size(dir_)
            local_dir = "%s%s" % ("/data", dir_)
            local = check_local_path(local_dir)
            write_file(output_remote_file, remote)
            write_file(output_local_file, local)


if __name__ == "__main__":
    main()
