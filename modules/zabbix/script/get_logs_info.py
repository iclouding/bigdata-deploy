# -*- coding: utf-8 -*-

import sys

sys.path.append("..")
import common
import os
import time
import socket
import ConfigParser
import pdb
import redis


def return_time( interval_type, interval, base_time=time.time()):
    if interval_type == 'hour':
        before = base_time - interval * 3600
    elif interval_type == 'day':
        before = base_time - interval * 3600 * 24
    return time.strftime("%Y-%m-%d-%H", time.localtime(before))


def get_time_list( interval_type, interval_values):
    time_list = list()
    for i in range(1, (interval_values + 1)):
        time_list.append(return_time( interval_type, i))
    return time_list


def get_hostname():
    return socket.gethostname()


def construct_filename(common_data, config_data):
    bash_path = config_data.get('path', None)
    projectname = config_data.get('project', None)
    interval_type = config_data.get('interval_type', None)
    interval_values = config_data.get('interval_values', None)
    files_suffix = common_data.get('files_suffix', None)


    filename_list = list()
    hostname = get_hostname()
    for timeinfo in get_time_list( interval_type, int(interval_values)):
        for num in range(2, (int(files_suffix) + 1)):
            filename = "log.%s.%s_%s_%s.log" % (projectname, timeinfo, hostname, num)
            full_file = os.path.join(bash_path, filename)
            filename_list.append(full_file)

    return filename_list


def return_section(files):
    cf = ConfigParser.SafeConfigParser()
    cf.read(files)
    sections = cf.sections()
    return sections


def check_isfile(all_files):
    file_l = list()
    for file in all_files:
        if not os.path.isfile(file):
            file_l.append(file)
    return file_l


def get_local_files(files):
    return_dict = dict()
    for one_file in files:
        local_size = os.path.getsize(one_file)
        return_dict[one_file] = local_size
    return return_dict


def main():
    expired = (3600 * 24 * 100)
    config_file = sys.argv[1]
    out_files = "local.error"
    all_files = list()
    common_data = common.get_section_values('common', config_file)
    sections = return_section(config_file)
    sections.remove('common')
    # pdb.set_trace()
    for section in sections:
        section_files = list()
        config_data = common.get_section_values(section, config_file)
        section_files = construct_filename(common_data, config_data)
        all_files += section_files

    # 本地文件比对
    miss_fils = check_isfile(all_files)
    real_files = list(set(all_files) - set(miss_fils))
    files_info = get_local_files(real_files)

    hostname = get_hostname()
    miss_files_key = "bigdata_monitor_miss_log_%s" % (time.strftime("%Y-%m-%d-%H", time.localtime()))
    files_info_key = "bigdata_monitor_log_%s_%s" % (hostname, time.strftime("%Y-%m-%d-%H", time.localtime()))

    # 连接redis
    r = redis.Redis(host=common_data['redis_host'], port=common_data['port'], db=common_data['db'])
    # 写入缺少文件信息
    # for item in miss_fils:
    #     r.rpush(miss_files_key, item)
    # r.expire(miss_files_key, expired)
    # import json
    if miss_fils:
        r.hset(miss_files_key, hostname, miss_fils)
        r.expire(miss_files_key, expired)

    # 写入文件大小信息到redis

    r.hmset(files_info_key, files_info)
    r.expire(files_info_key, expired)
    common.write_file_josn(out_files, miss_fils)


if __name__ == "__main__":
    main()
