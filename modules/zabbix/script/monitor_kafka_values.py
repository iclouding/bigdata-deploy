# -*- coding: utf-8 -*-

import pdb
from kafka_config import *
import sys
import redis
import time
from common import logMsg, bigdata_send_main


def get_values_redis(key, method='get'):
    r = redis.Redis(host=redis_host, port=port, db=db)
    if method == "get":
        data = r.get(key)
    elif method == "hgetall":
        data = r.hgetall(key)
    else:
        raise KeyError
    return data


def return_time_interval(time_values, interval):
    timeArray = time.strptime(time_values, "%Y%m%d%H")
    timeStamp = int(time.mktime(timeArray))
    timeOld = timeStamp - (3600 * interval)
    timeOldArray = time.localtime(timeOld)
    timeOldValues = time.strftime("%Y%m%d%H", timeOldArray)
    return timeOldValues


if __name__ == '__main__':
    lasttime = get_values_redis('lasttime', method='get')
    topicName = sys.argv[1].split(",")
    for one_topic in topicName:
        key_now = "%s_%s" % (one_topic, lasttime)
        data_now = get_values_redis(key_now, method='hgetall')
        if not monitor_time_interval.get(one_topic, None):
            msg = "topic could not find in config files:  %s " % one_topic
            logMsg("get config", msg, 2)
            raise KeyError

        time_old = return_time_interval(lasttime, int(monitor_time_interval[one_topic]))
        key_old = "%s_%s" % (one_topic, time_old)

        data_old = get_values_redis(key_old, method='hgetall')

        if (int(data_now['lag']) - int(data_old['lag'])) < int(monitor_values_interval[one_topic]):
            subjec = "%s 处理异常" % one_topic
            sendto = monitor_sendto[one_topic]
            body = "Kafka 数值存在异常"
            bigdata_send_main(sendto, subjec, body)
