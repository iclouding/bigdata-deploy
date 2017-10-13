# -*- coding: utf-8 -*-
import os
import time
import socket

base_dir = "/data/logs/logcenter/current"
local_project_names = ['eagle', 'helios', 'medusa']


def return_time(interval, base_time=time.time()):
    before = base_time - interval * 3600
    return time.strftime("%Y-%m-%d-%H", time.localtime(before))


def get_time_list():
    time_list = list()
    for i in range(0, 1):
        time_list.append(return_time(i))
    return time_list


def get_hostname():
    return socket.gethostname()


def str_filename():
    filename_list = list()
    hostname = get_hostname()
    for project_name in local_project_names:
        for timeinfo in get_time_list():
            for num in range(1, 4):
                filename = "log.%s.%s_%s_%s.log" % (project_name, timeinfo, hostname, num)
                filename_list.append(filename)
    return filename_list


def main():
    filenames = str_filename()
    no_found = list()
    for filename in filenames:
        log_file = os.path.join(base_dir, filename)
        if not os.path.isfile(log_file):
            no_found.append(log_file)
    print no_found


if __name__ == "__main__":
    main()
