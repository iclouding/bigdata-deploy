#!/usr/bin/env bash

LOGSTASH_HOME="$( cd "$( dirname "$0"  )" && cd .. && pwd  )"
echo "LOGSTASH_HOME is ${LOGSTASH_HOME}"
current_bin_path="`dirname "$0"`"
cd ${current_bin_path}

if [ $# -lt 1 ]; then
  echo "please input parameter like read_port_info.conf.conf"
  exit 1
fi

config_file_name=$1
echo "config_file_name is $config_file_name"
pid=$(ps -ef |grep ${config_file_name} |grep -v "grep"|grep -v "$0" |awk '{print $2}')
echo "pid is ${pid}"
if [ -z "${pid}" ]; then
    echo "pid is empty,start ${config_file_name} directly...."
    echo "start logstash ${config_file_name} on "`date` >> /data/logs/logstash/${config_file_name}_start_event.log
    nohup ${LOGSTASH_HOME}/bin/logstash -f ${LOGSTASH_HOME}/config/${config_file_name} --config.reload.automatic > /data/logs/logstash/${config_file_name}.log 2>&1 &
else
    echo "${config_file_name} is running,please stop it first"
fi


