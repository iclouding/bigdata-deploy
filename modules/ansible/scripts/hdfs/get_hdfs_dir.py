#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
抓取远程HDFS信息，写入文本
'''
import sys, os
from  common import read_files, write_file, run_cmd, return_day, logMsg

base_dir = "/backup/hdfs_backup"


def get_hdfs_path(path):
    current_path = "%s/%s" % (base_dir, path)
    cmd_mkdir = "mkdir -p %s" % current_path
    run_cmd(cmd_mkdir)
    get_cmd = "hadoop fs -get %s/* %s " % (path, current_path)
    msg = "get path %s" % path
    logMsg("get_path", msg, 1)
    run_cmd(get_cmd)


def main():
    filename = sys.argv[1]
    data = read_files(filename)
    for line in data.split('\n'):
        path = line.split(":")[0]
        day_num = line.split(":")[1]
        if int(day_num) == 0:
            current_path = path
            get_hdfs_path(current_path)
            continue
        for num in range(0, int(day_num)):
            current_path = path.replace('#{date}', str(return_day(num)))
            get_hdfs_path(current_path)
    print "GET ALL PATH"


if __name__ == "__main__":
    main()

