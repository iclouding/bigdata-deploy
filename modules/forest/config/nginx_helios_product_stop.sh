#!/usr/bin/env bash

current_bin_path="`dirname "$0"`"
cd ${current_bin_path}
echo "current_bin_path is ${current_bin_path}"

main_class="cn.whaley.turbo.forest.main.NginxHeliosLogProcessingApp"

pid=$(ps -ef |grep ${main_class} |grep -v grep |awk '{print $2}')
echo "pid is ${pid}"

if [ -z "${pid}" ]; then
    echo "no ${main_class} process exist and exit...."
    exit 0
else
  echo "start kill -15 ${pid} and wait forest to consume last record.."
  kill -15 ${pid}
  echo "loop 3 times to wait forest stop...."
  counter=3
  while [ ${counter} -gt 0 ]
  do
     echo "counter is ${counter}"
     counter=$(( $counter - 1 ))
     pro_num=`ps -ef|grep ${main_class} |grep ${pid} |grep -v grep|wc -l`
     echo "pro_num is $pro_num"
     if [ ${pro_num} -gt 0 ]; then
        echo "${main_class} is still exist,need wait more time"
        sleep 10s
     else
        break
     fi
  done


  echo "check if need kill -9 to kill forest"
  pro_num=`ps -ef | grep ${main_class} | grep ${pid} | grep -v grep|wc -l`
  echo "pro_num is $pro_num"
  if [ ${pro_num} -gt 0 ]; then
      echo "${main_class} is still exist,need to kill -9 "
      kill -9 ${pid}
    else
      echo "not need to use kill -9"
  fi
fi
