#!/usr/bin/env bash

JAVA_HOME=/usr/local/bin/java
${JAVA_HOME}/bin/jps -ml|grep kylin|grep org.apache.catalina.startup.Bootstrap|awk '{print $1}'|xargs kill

for (( c=1; c<=50; c++ ))
do
  pro_num=`netstat -nltp|grep 7070|wc -l`
  echo "pro_num is ${pro_num}"
  if [ ${pro_num} -gt 0 ]; then
     echo "wait $c second for kylin stop"
     sleep 1s
  else
     break
  fi
done

pro_num=`netstat -nltp|grep 7070|wc -l`
if [ ${pro_num} -lt 1 ]; then
  echo "need restart kylin."`date`
  . /etc/profile;sh /opt/kylin/bin/kylin.sh start
fi