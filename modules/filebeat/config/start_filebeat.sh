#!/usr/bin/env bash
current_bin_path="`dirname "$0"`"
echo "current_bin_path is ${current_bin_path}"
cd ${current_bin_path}

config_name=$1

if [ "$config_name" = "" ]
then
  echo "config_name is not set! exit...."
  exit 1
else
  echo "config_name is ${config_name}!"
fi

pro_num=`ps -ef|grep "$config_name"|grep -v grep|wc -l`
echo "pro_num is $pro_num"
if [ ${pro_num} -gt 0 ]; then
  echo "filebeat is already exist,no need to restart"
  exit 1
else
  nohup ./filebeat -c ../conf/"$config_name" >> /data/logs/filebeat/filebeat_${config_name}.log 2>&1 &
  echo "start filebeat...."`date` >>/data/logs/filebeat/filebeat_${config_name}_start_event.log
fi