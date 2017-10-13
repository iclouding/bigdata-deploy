#!/usr/bin/env bash
current_bin_path="`dirname "$0"`"
echo "current_bin_path is ${current_bin_path}"
cd ${current_bin_path}
ps -ef|grep filebeat_nginx_medusa_3x.yml|grep -v grep|awk '{print $2}'|xargs kill  -15

sleep 3s

pro_num=`ps -ef|grep filebeat_nginx_medusa_3x.yml|grep -v grep|wc -l`
echo "after kill -15, pro_num is $pro_num"
