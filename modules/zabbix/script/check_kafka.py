#!/usr/bin/env python
from kafka.client import SimpleClient
from kafka.consumer import KafkaConsumer
from kafka.consumer import SimpleConsumer
from kazoo.client import KazooClient
from kafka.consumer import base
from kafka.structs import (
    OffsetRequestPayload, OffsetCommitRequestPayload, OffsetFetchRequestPayload)
import sys



# zookeepers="10.10.217.152:2182"
zookeepers = "127.0.0.1:2182"

kafka = "127.0.0.1:9092"

group = "consumer-group"

if __name__ == '__main__':

    broker = SimpleClient(kafka)
    lags = {}
    zk = KazooClient(hosts=zookeepers, read_only=True)
    zk.start()
    logsize = 0
    #    topics=zk.get_children("/consumers/%s/owners" % (group) )
    topic = sys.argv[1]
    data_need = sys.argv[2]
    #    for topic in topics:
    if topic:
        logsize = 0
        #	print topic
        partitions = broker.get_partition_ids_for_topic(topic)
        #	print partitions
        consumer = KafkaConsumer(broker, group, str(topic))
        responses = broker.send_offset_fetch_request(group, [OffsetFetchRequestPayload(topic, p) for p in partitions],
                                                     fail_on_error=True)
        #	print responses
        latest_offset = 0
        for res in responses:
            if topic != "test":
                latest_offset += res[2]
            #	print latest_offset
        for partition in partitions:
            log = "/consumers/%s/offsets/%s/%s" % (group, topic, partition)
            if zk.exists(log):
                data, stat = zk.get(log)
                logsize += int(data)
            #	print logsize
        lag = latest_offset - logsize
    #	print lag
    broker.close()
    zk.stop()
    zk.close()
    if data_need == "offset":
        print latest_offset
    elif data_need == "logsize":
        print logsize
    elif data_need == "lag":
        print lag
    else:
        sys.exit()
