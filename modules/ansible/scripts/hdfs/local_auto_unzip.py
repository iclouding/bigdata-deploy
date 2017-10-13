#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
读取参数（目录），列出目录下所有tar.gz结尾的文件，逐个对文件执行解压缩操作
'''
import os
import sys
from common import logMsg, run_cmd, read_files
import pdb


def get_local_list(dirs, suffix):
    return_list = list()
    items = os.listdir(dirs)
    for item in items:
        files = "%s/%s" % (dirs, item)
        if os.path.isfile(files):
            length = len(suffix)
            if files[-length:] == suffix:
                return_list.append(files)
    return return_list


def uncomp(files):
    cmd = "tar zxvf %s" % files
    run_cmd(cmd)


def main():
    dirs = sys.argv[1]
    suffix = "tar.gz"
    files = get_local_list(dirs, suffix)
    for com_file in files:
        uncomp(com_file)

    print "all files uncomp"

if __name__ == "__main__":
    main()
