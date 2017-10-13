#!/usr/bin/env bash

current_bin_path="`dirname "$0"`"
cd ${current_bin_path}

topic_name=$1

#阀值设定为5分钟
threshold_value=300

process_number=`ps -ef|grep "$0"|grep $topic_name|grep -v "grep"|wc -l`
echo "process_number:${process_number}"
if [ ${process_number} -gt 2 ]; then
  echo "process exist,exit"
  exit 0
else
  echo "start running"
fi


sh /opt/kafka3/bin/kafka-console-consumer.sh --topic $topic_name  -bootstrap-server bigdata-appsvr-130-1:9094 | head -1 > ${topic_name}_log_content
logTime=`cat ${topic_name}_log_content | awk -F '"datetime":"' '{print $2}'|awk -F '","' '{print $1}'`
timestamp_now=`date +%s`
timestamp_in_log=`date -d "$logTime" +%s`
let second_diff=($timestamp_now - $timestamp_in_log)

if [ ${second_diff} -gt ${threshold_value} ]; then
  echo "delay more than ${threshold_value},now is ${second_diff}"
  python sendMail.py ${topic_name} ${second_diff}
else
  echo "second_diff:${second_diff}"
fi


*/15 * * * * source /etc/profile;sh /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin/monitor_process_delay.sh medusa-processed-log > /dev/null 2>&1
*/16 * * * * source /etc/profile;sh /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin/monitor_process_delay.sh helios-processed-log > /dev/null 2>&1