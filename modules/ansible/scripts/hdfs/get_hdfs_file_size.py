#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
抓取远程HDFS遍历目录下所有的文件，将其大小写入文本
'''
import sys, os
from  common import write_file, run_cmd


def get_hdfs_list(path):
    return_dict = dict()
    cmd = "hadoop fs -ls -R %s" % path
    output = run_cmd(cmd)
    for line in output.split("\n"):
        if len(line.split()) == 8:
            filename = line.split()[7]
            size = line.split()[4]
            return_dict[filename] = size
    return return_dict


def write_file_by_dict(filename, dict_values):
    for key in dict_values.keys():
        msg = "%s#&#%s" % (key, dict_values[key])
        write_file(filename, msg)
    return True


def main():
    path = sys.argv[1]
    outfile = sys.argv[2]
    filename_dict = get_hdfs_list(path)
    write_file_by_dict(outfile, filename_dict)

    print "Get all files in %s complete" % path


if __name__ == "__main__":
    main()
