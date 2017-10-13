# -*- coding: utf-8 -*-
'''
检查配置文件中的HDFS目录，如果文件名存在匹配的关键词，记录日志，删除当前目录下所有文件，将匹配到的目录写入另一目录
'''

import os
import sys
from common import logMsg, run_cmd, read_files, write_file
import pdb

key_word = "_COPYING_"
output_file = "need_recopy.log"


def check_hdfs_dirs(path):
    cmd = "hadoop fs -ls -R %s" % path
    data = run_cmd(cmd)
    items = data.split("\n")
    remove_path = list()

    for lines in items:
        # 首先判断输出内容是否匹配规则like        "-rw-r--r--   3 hdfs supergroup          0 2017-02-28 13:30 /temp/aa/a1/miles_COPYING_"
        if len(lines.split() == 8):
            if key_word in lines:
                full_files = lines.split()[-1]
                remove_path.append(os.path.split(full_files)[0])
        return remove_path


def remove_hdfs_dirs(path):
    cmd = "hadoop fs -rm %s/*" % path
    run_cmd(cmd)


def main():
    config = sys.argv[1]
    data = read_files(config).split("\n")
    remove_list = list()
    for line in data:
        remove_list = check_hdfs_dirs(line)
    for item in remove_list:
        write_file(output_file, item)
        remove_hdfs_dirs(item)


if __name__ == "__main__":
    main()
