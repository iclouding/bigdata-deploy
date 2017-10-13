#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
连凯需要的脚本，用于将HDFS上的目录逐个下载，打成tar包
'''
import os
import sys
from common import run_cmd, read_files, logMsg
import pdb

bash_path = "/backup/tar_files"


def get_sub_dir(path):
    #pdb.set_trace()
    return_list = list()
    items = os.listdir(path)
    for item in items:
        curr_path = "%s/%s" % (path, item)
        if os.path.isdir(curr_path):
            return_list.append(curr_path)

    return return_list


def make_tar_file(path_list):
    for path in path_list:
        suffix_file = path.replace('/', '_') + ".tar.gz"
        cmd = "cd %s && tar zcvfP %s %s" % (bash_path, suffix_file, path)
        msg = "Start tar %s" % path
        logMsg("make_tar", msg, 1)
        run_cmd(cmd)


def make_tar_workflow(filename):
    data = read_files(filename)
    path_list = list()
    #pdb.set_trace()
    for line in data.split("\n"):
        path_ = line.split(":")[0]
        item = line.split(":")[1]
        if int(item) == 1:
            sub_paths = get_sub_dir(path_)
            for sub_path in sub_paths:
                path_list.append(sub_path)
        elif int(item) == 0:
            path_list.append(path_)
    make_tar_file(path_list)


if __name__ == "__main__":
    config_file = sys.argv[1]
    make_tar_workflow(config_file)
