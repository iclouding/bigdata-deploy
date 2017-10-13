#!/usr/bin/env bash
current_bin_path="`dirname "$0"`"
echo "current_bin_path is ${current_bin_path}"
cd ${current_bin_path}

pro_num=`ps -ef|grep filebeat_helios_raw_log.yml|grep -v grep|wc -l`
echo "filebeat_helios_raw_log,pro_num is $pro_num"
