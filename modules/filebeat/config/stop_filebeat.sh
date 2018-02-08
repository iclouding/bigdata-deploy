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

ps -ef|grep -e '/filebeat'|grep "$config_name"|grep -v grep|grep -v "$0"
pro_num=`ps -ef|grep -e '/filebeat'|grep "$config_name"|grep -v grep|grep -v "$0"|wc -l`
echo "pro_num is $pro_num"
if [ ${pro_num} -gt 0 ]; then
  ps -ef|grep ${config_name}|grep -v grep|awk '{print $2}'|xargs kill
  sleep 3s
  pro_num=`ps -ef|grep ${config_name}|grep -v grep|grep -v "$0"|wc -l`
  echo "after kill -15, pro_num is $pro_num"
else
  echo "filebeat is not exist,no need to stop"
  exit 1
fi

