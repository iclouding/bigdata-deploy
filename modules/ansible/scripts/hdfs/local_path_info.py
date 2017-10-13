#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
from commons import read_files, logMsg, run_cmd, write_file


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


def write_dict(files, dict_):
    for key in dict_.keys():
        line = "%s#&#%s\n" % (key, dict_[key])
        write_file(files, line)


def main():
    path = sys.argv[1]
    output_files = sys.argv[2]
    dict_ = check_local_path(path)
    write_dict(output_files, dict_)


if __name__ == "__main__":
    main()
