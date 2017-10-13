#!/bin/bash

Day=`date -d '0 day ago' +%Y%m%d`

BIN_HOME=/opt/logupload
DATA_HOME=/data/backups/moretv_loginlog/
HADOOP_HOME=/opt/hadoop

$BIN_HOME/moretvloginlog.sh $Day

$HADOOP_HOME/bin/hadoop fs -mkdir -p /log/moretvloginlog/rawlog/$Day
$HADOOP_HOME/bin/hadoop fs -put $DATA_HOME/loginlog.access.log_$Day* /log/moretvloginlog/rawlog/$Day

#/opt/bi/log2parquet/sbin/MoretvLoginLog2Parquet.sh $Day 1
