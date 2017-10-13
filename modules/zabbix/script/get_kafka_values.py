# -*- coding: utf-8 -*-

# !/usr/bin/env python
from kafka.client import SimpleClient
from kazoo.client import KazooClient
from kafka.structs import OffsetFetchRequestPayload
from kafka_config import *
from common import logMsg
import redis
import json
import time


class Mykafa():
    def __init__(self, zk_conn, kafka_conn):
        self.zk_conn = zk_conn
        self.kafka_conn = kafka_conn
        self.topic_sub = ['lag', 'logsize', 'offset']

    def get_values_kafak(self, groupName, topicName):
        kafka_values = dict()
        broker = SimpleClient(kafka_conn)
        zk = KazooClient(hosts=zookeepers_conn, read_only=True)
        zk.start()
        logsize = 0
        if topicName:
            logsize = 0
            partitions = broker.get_partition_ids_for_topic(topicName)
            responses = broker.send_offset_fetch_request(groupName,
                                                         [OffsetFetchRequestPayload(topicName, p) for p in partitions],
                                                         fail_on_error=True)
            latest_offset = 0
            for res in responses:
                if topicName != "test":
                    latest_offset += res[2]
            for partition in partitions:
                log = "/consumers/%s/offsets/%s/%s" % (groupName, topicName, partition)
                if zk.exists(log):
                    data, stat = zk.get(log)
                    logsize += int(data)
            lag = latest_offset - logsize
        broker.close()
        zk.stop()
        zk.close()
        kafka_values['offset'] = latest_offset
        kafka_values['logsize'] = logsize
        kafka_values['lag'] = lag
        return kafka_values


def write_kafka_redis(key, values, method='set'):
    r = redis.Redis(host=redis_host, port=port, db=db)
    if method == 'set':
        r.set(key, values)
    elif method == "hmset":
        try:
            r.hmset(key, values)
            r.expire(key, redis_expired)
        except:
            msg = "Write key %s error values %s" % (key, json.dumps(values))
            logMsg("write_redis", msg, 2)
            raise IOError
    else:
        raise KeyError


if __name__ == '__main__':
    time_string = time.strftime("%Y%m%d%H", time.localtime())
    write_kafka_redis('lasttime', time_string)
    mykafka = Mykafa(zookeepers_conn, kafka_conn)
    for groupName in kafka_info.keys():
        for topicName in kafka_info[groupName]:
            kafka_values = mykafka.get_values_kafak(groupName, topicName)
            redis_key = "%s_%s" % (topicName, time_string)
            write_kafka_redis(redis_key, kafka_values, method='hmset')
