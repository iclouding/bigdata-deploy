#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
抓取远程HDFS信息，写入文本
'''
import sys, os
from  common import read_files, write_file, run_cmd, return_day

base_dir = "/data/scripts"


def get_hdfs_list(path):
    return_dict = dict()
    cmd = "hadoop fs -du -s %s" % path
    output = run_cmd(cmd)
    if output:
        return_dict[output.split()[1]] = output.split()[0]
    else:
        return_dict[path] = 0
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
    outfile = "remote.log"
    data = read_files(filename)
    for line in data.split('\n'):
        path = line.split(":")[0]
        day_num = line.split(":")[1]
        if int(day_num) == 0:
            current_path = path
            output_dict = get_hdfs_list(current_path)
            write_file_by_dict(outfile, output_dict)
            #total_num += sum_by_dict(output_dict)
        else:
            for num in range(0, int(day_num)):
                current_path = path.replace('#{date}', str(return_day(num)))
                output_dict = get_hdfs_list(current_path)
                write_file_by_dict(outfile, output_dict)
                #total_num += sum_by_dict(output_dict)
   # print "Total num :%d byte" % total_num


if __name__ == "__main__":
    main()

