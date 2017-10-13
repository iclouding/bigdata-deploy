#!/usr/bin/env bash
current_bin_path="`dirname "$0"`"
echo "current_bin_path is ${current_bin_path}"
cd ${current_bin_path}

pro_num=`ps -ef|grep filebeat_log_raw_whaleytv_log.yml|grep -v grep|wc -l`
echo "pro_num is $pro_num"
if [ ${pro_num} -gt 0 ]; then
  echo "filebeat is already exist,no need to restart"
  exit 1
else
  nohup ./filebeat -c filebeat_log_raw_whaleytv_log.yml >> /home/spark/cdh/filebeat_log_raw_whaleytv_log.log 2>&1 &
fi
