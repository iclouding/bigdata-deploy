#!/bin/sh
source /etc/profile
source ~/.bash_profile
cd `dirname $0`
pwd=`pwd`
time=`date '+%Y-%m-%d %H:%M:%S'`
day=`date '+%Y-%m-%d'`
currentTime=`date +%s`
yesterday=`date -d "1 days ago" +%Y-%m-%d`
echo "currentTime is $time " >> /data/logs/WhaleyThorProbe/${day}.log
classpath=$pwd/WhaleyThorProbe.jar
java -classpath $classpath  com.whaley.main.ThorProbeTop100  "$yesterday"   >> /data/logs/WhaleyThorProbe/${day}.log
