#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
from commons import read_files, logMsg, run_cmd


def safe_rm_directory(item):
    cmd_step1 = "rm -f %s/*" % item
    run_cmd(cmd_step1)
    cmd_step2 = "rmdir %s" % item
    run_cmd(cmd_step2)
    msg = "Safe RM %s success " % item
    logMsg("rm", msg, 1)
    return True


def main():
    config_name = sys.argv[1]
    directory_values = read_files(config_name).split('\n')
    for directory in directory_values:
        safe_rm_directory(directory)

    print "RM all items"


if __name__ == "__main__":
    main()
