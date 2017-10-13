# -*- coding: utf-8 -*-
import sys
import os
from common import read_file

base_dir = "/etc/zabbix/script"

if __name__ == "__main__":
    section = sys.argv[1]
    keys = sys.argv[2]

    file_name = "%s/redis/%s/%s" % (base_dir, section, keys)
    if not os.path.isfile(file_name):
        data = '0'
    else:
        data = read_file(file_name)
    print data
