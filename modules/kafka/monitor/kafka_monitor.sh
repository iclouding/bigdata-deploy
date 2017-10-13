#!/usr/bin/env bash

#put this script in kafka/bin directory,and config it in cron job to monitor kafka 0.10 service.
#dependency is JAVA_HOME/bin/jps in PATH

current_bin_path="`dirname "$0"`"
cd ${current_bin_path}
echo "current_bin_path is ${current_bin_path}"
main_class="kafka.Kafka"
key_word="config/server.properties"

echo "jps -ml |grep ${main_class} | grep ${key_word} "
pid=$(jps -ml |grep ${main_class} | grep ${key_word} |grep -v grep |awk '{print $1}')
echo "pid is ${pid}"

if [ -z "${pid}" ]; then
    echo "pid is empty,need start ${main_class} ...."
    echo "sh ${current_bin_path}/kafka-server-start.sh -daemon ${current_bin_path}/../config/server.properties"
    sh ${current_bin_path}/kafka-server-start.sh -daemon ${current_bin_path}/../config/server.properties
    sleep 10s
    pid=$(jps -ml |grep ${main_class} | grep ${key_word} |grep -v grep |awk '{print $1}')
    echo "after start,pid is ${pid}"
  else
    echo "pid is ${pid} ,no need to start ${main_class},current date: "`date`
fi


#monitor kafka server
#*/10 * * * * . /home/hadoop/.bash_profile;sh /hadoopecosystem/kafka/bin/kafka_monitor.sh >> /hadoopecosystem/kafka/logs/start_server.log 2>&1

