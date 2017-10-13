#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
删除过期目录下的文件
'''
import os
import sys
from common import logMsg, run_cmd, read_files, write_file
import pdb


def get_expired_list(path, expired_values):
    return_list = list()
    #pdb.set_trace()
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for one_dir in dirs:
                if one_dir[-9:] in expired_values:
                    return_list.append(os.path.join(root, one_dir))
    return return_list


def main():
    dirs = sys.argv[1]
    expired_values = ['20170227', '20170226', '20170225', '20170224', '20170223']
    expired_dirs = get_expired_list(dirs, expired_values)
    # 计算出的过期日志写入文件
    expired_log = "expired.log"
    for dirs in expired_dirs:
        write_file(expired_log, dirs)
    # mv 过期目录到另一个目录
    suffix = "/data/temp/backup/hdfs_backup"
    target = "/data/backups/expired"
    for dirs in expired_dirs:
        target_dirs = dirs.replace(suffix, target)[:-9]
        mv_cmd = "mv %s %s" % (dirs, target_dirs)
        print(mv_cmd)
        # run_cmd(mv_cmd)

    print "all expired files remove"


if __name__ == "__main__":
    main()
