#!/bin/bash

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 20  --topic MoreTV_FrontPage

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 10  --topic Helios_FrontPage

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 5  --topic Helios_MusicList

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 10  --topic MoreTV_MusicList

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 15  --topic MoreTV_FrontPageTagsHot

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 15  --topic MoreTV_FrontPageTagsMovie

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 15  --topic MoreTV_ReturnTagsHot

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 15  --topic MoreTV_ReturnTagsMovie

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 10  --topic MoreTV_PeopleAlsoLike

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 3  --topic Helios_Rec4Search_TopVideo

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 6  --topic Helios_Rec4Search_UserTopContentType


sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 3  --topic Helios_SearchHot

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 10  --topic Helios_GuessYouLike

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 10  --topic Helios_PeopleAlsoLike

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 20  --topic MoreTV_GuessYouLike

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 4  --topic RankingList

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 4  --topic MoreTV_SearchHot

sh /opt/kafka2/bin/kafka-topics.sh --create --zookeeper bigdata-appsvr-130-5:2182 --replication-factor 2 --partitions 7  --topic Search_vv