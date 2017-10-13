#!/bin/bash

Day=`date -d '0 day ago' +%Y%m%d`

BIN_HOME=/opt/logupload
DATA_HOME=/data/backups/mtvkids_loginlog/
HADOOP_HOME=/opt/hadoop

$BIN_HOME/mtvkidsloginlog.sh $Day

$HADOOP_HOME/bin/hadoop fs -mkdir -p /log/mtvkidsloginlog/rawlog/$Day
$HADOOP_HOME/bin/hadoop fs -put $DATA_HOME/mtvkidsloginlog.access.log_$Day* /log/mtvkidsloginlog/rawlog/$Day

#/opt/bi/log2parquet/sbin/MtvkidsLoginLog2Parquet.sh $Day 1
