#!/bin/bash

sh /opt/kafka1/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2181 --replication-factor 2 --partitions 20  --topic MoreTV_FrontPage

sh /opt/kafka1/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2181 --replication-factor 2 --partitions 10  --topic Helios_FrontPage

sh /opt/kafka1/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2181 --replication-factor 2 --partitions 5  --topic Helios_MusicList

sh /opt/kafka1/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2181 --replication-factor 2 --partitions 10  --topic MoreTV_MusicList

sh /opt/kafka1/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2181 --replication-factor 2 --partitions 15  --topic Play_stats

sh /opt/kafka1/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2181 --replication-factor 2 --partitions 15  --topic Real_time_recommend