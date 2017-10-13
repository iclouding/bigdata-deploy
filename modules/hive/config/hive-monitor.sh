#!/usr/bin/env bash

#put this script in HIVE_HOME/bin directory,and config it in cron job to monitor hive meta  store service.

current_bin_path="`dirname "$0"`"
cd ${current_bin_path}
echo "current_bin_path is ${current_bin_path}"
main_class="org.apache.hadoop.hive.metastore.HiveMetaStore"

pid=$(ps -ef |grep ${main_class} |grep -v grep |awk '{print $2}')

if [ -z "${pid}" ]; then
    echo "pid is empty,need start ${main_class} ...."
    nohup ./hive --service metastore > metastore.log 2>&1 &
    sleep 3s
    pid=$(ps -ef |grep ${main_class} |grep -v grep |awk '{print $2}')
    echo "after start,pid is ${pid}"
  else
    echo "pid is ${pid} ,no need to start ${main_class},current date: "`date`
fi

#*/10 * * * * . /home/hadoop/.bash_profile;sh /hadoopecosystem/hive/bin/hive_monitor.sh >> /hadoopecosystem/hive/logs/metastore.log 2>&1

