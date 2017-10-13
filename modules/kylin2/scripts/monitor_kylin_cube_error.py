# -*- coding: utf-8 -*-
import json
import requests
from requests.auth import HTTPBasicAuth
import sys
import logging
import time

'''
脚本作用：监控kylin1.6版本存在的读取kafka0.10出错，导致cube构建失败的任务，作为补丁存在
输入参数:cube名称 【例如：MEDUSA_PLAY_LIVE_QOS_CUBE】
使用方式：python monitor_kylin_cube_error_satus.py MEDUSA_PLAY_LIVE_QOS_CUBE
部署机器：bigdata-appsvr-130-1
执行用户：hadoop
执行频率：暂定每2分钟运行检测一次
运行方式：cronjob
*/2 * * * * /bin/python /home/hadoop/monitor_kylin_cube_error_satus.py MEDUSA_PLAY_LIVE_QOS_CUBE >>/data/logs/kylin/MEDUSA_PLAY_LIVE_QOS_CUBE_MONITOR.log 2>&1
现有监控cube如下：
MEDUSA_PLAY_LIVE_QOS_CUBE
helios_rolling_status_cube
medusa_hot_play_cube
hot_play_cube
whaley_thor_probe_cube
'''


def logMsg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = None
    logger = logging.getLogger()
    # logname = sys.argv[0] + '.log'
    logname = "/data/logs/kylin/monitor_kylin_cube_error.log"
    hdlr = logging.FileHandler(logname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)  # 网络上的实现基本为说明这条语句的使用和作用


def get_status(cube_name):
    while 1:
        url = "http://bigdata-appsvr-130-1:7070/kylin/api/jobs"
        parameters = {'cubeName': cube_name, "limit": 15, "offset": 0, "projectName": "stream", "status": 8,
                      "timeFilter": 1}
        P_get = requests.get(url, params=parameters, auth=HTTPBasicAuth('ADMIN', 'KYLIN'))
        i = 0

        if P_get.status_code == 200:
            return json.loads(P_get.text)
        else:
            i += 1
            if i > 4:
                msg = "get url failed "
                logMsg("get_url", msg, 2)
                return False
            else:
                time.sleep(10)


def check_status(data):
    if (len(data) > 0):
        for oneStr in data:
            if 'name' not in oneStr.keys():
                msg = "name key not in json"
                logMsg("check", msg, 2)
            elif ('MERGE' not in oneStr['name']):
                msg = "Find error cube %s, resume!!" % oneStr["name"]
                logMsg("check", msg, 2)
                uuid = oneStr["uuid"]
                url = 'http://bigdata-appsvr-130-1:7070/kylin/api/jobs/' + uuid + '/resume'
                requests.put(url, auth=HTTPBasicAuth('ADMIN', 'KYLIN'))
    else:
        msg = "return parsed_json is null"
        logMsg("check", msg, 2)
        return False


def main():
    cub_list = sys.argv[1].split(',')
    for cub_one in cub_list:
        msg = "start check %s" % cub_one
        logMsg("start", msg, 1)
        parsed_json = get_status(cub_one)
        if parsed_json:
            check_status(parsed_json)


if __name__ == "__main__":
    main()
