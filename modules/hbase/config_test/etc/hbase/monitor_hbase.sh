#!/usr/bin/env bash

app_name=""
short_name=""
usage="Usage: sh monitor_hbase.sh org.apache.hadoop.hbase.regionserver.HRegionServer regionserver"
# if no args specified, show usage
if [ $# -eq 2 ]; then
   app_name=$1
   short_name=$2
   echo "app_name is ${app_name}"
   echo "short_name is ${short_name}"
else
  echo 'please input app_name,short_name like org.apache.hadoop.hbase.regionserver.HRegionServer regionserver'
  echo ${usage}
  exit 1
fi

current_bin_path="`dirname "$0"`"
echo "current_bin_path is ${current_bin_path}"
cd ${current_bin_path}

pro_num=`ps -ef|grep "${app_name}"|grep -v grep|grep -v "$0" |wc -l`
echo "pro_num is $pro_num"
if [ ${pro_num} -gt 0 ]; then
  echo "${short_name} is already exist,no need to start"
  exit 1
else
  if [ "${short_name}"x == "regionserver"x ]; then
    echo "start ${short_name} ...."
    sh /opt/hbase/bin/hbase-daemon.sh start ${short_name}
  elif [ "${short_name}"x == "master"x ]; then
    echo "start ${short_name} ...."
    sh /opt/hbase/bin/hbase-daemon.sh start ${short_name}
  fi
  echo "start ${short_name}"`date` >> /data/logs/hbase/restart.log
fi

# */6 * * * * sh /opt/hbase/bin/monitor_hbase.sh org.apache.hadoop.hbase.regionserver.HRegionServer regionserver >/dev/null 2>&1
# */6 * * * * sh /opt/hbase/bin/monitor_hbase.sh org.apache.hadoop.hbase.master.HMaster master >/dev/null 2>&1
