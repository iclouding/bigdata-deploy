#!/usr/bin/env bash

LOGSTASH_HOME="$( cd "$( dirname "$0"  )" && cd .. && pwd  )"
echo ${LOGSTASH_HOME}
current_bin_path="`dirname "$0"`"
cd ${current_bin_path}

if [ $# -lt 1 ]; then
  echo "please input parameter like read_port_info.conf"
  exit 1
fi

config_file_name=$1
echo "start to stop ${config_file_name} ...."
pid=$(ps -ef |grep -e '/logstash'|grep ${config_file_name} |grep -v "grep"|grep -v "$0"  |awk '{print $2}')
echo "pid is ${pid}"

if [ -z "${pid}" ]; then
    echo "pid is empty,not need to stop this process"
    exit 0
fi

echo "start kill -15 ${pid} and wait ${config_file_name} to stop.."
kill -15 ${pid}

echo "loop 3 times to wait ${config_file_name} stop...."
counter=3
while [ ${counter} -gt 0 ]
do
   echo "counter is ${counter}"
   counter=$(( $counter - 1 ))
   pro_num=`ps -ef|grep ${config_file_name} |grep ${pid} |grep -v grep|wc -l`
   echo "pro_num is $pro_num"
   if [ ${pro_num} -gt 0 ]; then
        echo "${config_file_name} is still exist,need wait more time"
        sleep 10s
     else
        break
   fi
done


echo "check if need kill -9 to kill ${config_file_name}"
pro_num=`ps -ef | grep ${config_file_name} | grep ${pid} | grep -v grep|wc -l`
echo "pro_num is $pro_num"
if [ ${pro_num} -gt 0 ]; then
    echo "${config_file_name} is still exist,need to kill -9 "
    kill -9 ${pid}
  else
    echo "not need to use kill -9"
fi