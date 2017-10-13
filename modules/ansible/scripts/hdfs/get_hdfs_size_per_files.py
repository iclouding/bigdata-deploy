#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
抓取远程HDFS信息，读取每个文件大小，写入文本
'''
import sys, os
from  common import read_files, write_file, run_cmd, return_day, logMsg

base_dir = "/temp_data"
errorlog = "hdfs_err.log"


def get_hdfs_list(path):
    return_dict = dict()
    hdfs_path = "%s%s" % (base_dir, path)
    cmd = "hadoop fs -ls -R %s" % hdfs_path
    output = run_cmd(cmd)
    try:
        for line in output.split("\n"):
            if len(line.split()) == 8:
                filename = line.split()[7]
                size = line.split()[4]
                return_dict[filename] = size
    except:
        msg = "Clount`t get path %s" % hdfs_path
        print msg
    return return_dict


def write_file_by_dict(filename, dict_values):
    for key in dict_values.keys():
        msg = "%s#&#%s" % (key, dict_values[key])
        write_file(filename, msg)
    return True


def sum_by_dict(dict_values):
    total = 0
    for key in dict_values.keys():
        total += int(dict_values[key])
    return total


def main():
    filename = sys.argv[1]
    total_num = 0
    outfile = sys.argv[2]
    data = read_files(filename)
    for line in data.split('\n'):
        path = line.split(":")[0]
        day_num = line.split(":")[1]
        if int(day_num) == 0:
            current_path = path
            output_dict = get_hdfs_list(current_path)
            write_file_by_dict(outfile, output_dict)
            # total_num += sum_by_dict(output_dict)
        else:
            for num in range(0, int(day_num)):
                new_num = int(num) + 3
                current_path = path.replace('#{date}', str(return_day(new_num)))
                output_dict = get_hdfs_list(current_path)
                write_file_by_dict(outfile, output_dict)
                # total_num += sum_by_dict(output_dict)
    print "Mission complete!"


if __name__ == "__main__":
    main()
