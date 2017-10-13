# -*- coding: utf-8 -*-
import requests
import time


def active_url():
    url = "http://127.0.0.1:5001/monitor_loginfo"
    r = requests.get(url)
    # print r.status_code


def read_file(files):
    with open(files, 'r') as f:
        data = f.read()
    return data.strip()


if __name__ == "__main__":
    active_url()
    time.sleep(1)
    files = "/tmp/loginfo.log"
    num = read_file(files)
    print num
