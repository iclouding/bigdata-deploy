#!/usr/bin/env bash

#----------------------help----------------------
#this script is used to monitor the kylin

pro_num=`netstat -nltp|grep 7070|wc -l`

if [ ${pro_num} -lt 1 ]; then
  echo "need restart kylin."`date`
  sh /opt/kylin/bin/kylin.sh start
else
  echo "kylin is ok."
fi