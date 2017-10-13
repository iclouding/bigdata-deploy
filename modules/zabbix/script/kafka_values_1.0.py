# -*- coding: utf-8 -*-
import os, sys, time, json, yaml
from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
from kafka import (KafkaClient, KafkaConsumer)
from kafka.client import SimpleClient
import pdb

zookeepers_conn = "10.255.130.1:2182"
kafka_conn = "10.255.130.1:9093"


def get_offset(group, topicname):
    try:
        kafka_client = KafkaClient(kafka_conn, timeout=30)
    except Exception as e:
        print "Error, cannot connect kafka broker."
        sys.exit(1)
    else:
        kafka_topics = kafka_client.topics
    finally:
        kafka_client.close()

    try:
        zookeeper_client = KazooClient(hosts=zookeepers_conn, read_only=True, timeout=30)
        zookeeper_client.start()
    except Exception as e:
        print "Error, cannot connect zookeeper server."
        sys.exit(1)

    offset_total = 0
    logsize_totoal = 0
    broker = SimpleClient(kafka_conn)
    # partition_path = 'consumers/%s/offsets/%s' % (group, topicname)
    partitions = broker.get_partition_ids_for_topic(topicname)
    kafka_consumer = KafkaConsumer(bootstrap_servers=kafka_conn)

    for partition in partitions:
        base_path = 'consumers/%s/%s/%s/%s' % (group, '%s', topicname, partition)
        owner_path, offset_path = base_path % 'owners', base_path % 'offsets'
        pdb.set_trace()
        offset = zookeeper_client.get('/' + offset_path)[0]
        offset_total += int(offset)

        # logsize_num = kafka_consumer.get_partition_offsets(topicname, partition, -1, 1)[0]
        # logsize_totoal += int(logsize_num)

    return offset_total, logsize_totoal


def main():
    group = 'moretv'
    topicname = "MoreTV_TimeDividedFrontPage"
    get_offset(group, topicname)


if __name__ == "__main__":
    main()
