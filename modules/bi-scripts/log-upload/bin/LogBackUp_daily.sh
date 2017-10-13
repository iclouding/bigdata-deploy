#!/usr/bin/env bash

cd `dirname $0`
pwd=`pwd`

LogDate=$1
if [ -z "$LogDate" ]; then
    LogDate=`date -d '1 hour ago' +%Y-%m-%d`
fi

HostName=`hostname`
LogcenterDir="/data/logs/logcenter/current"

LogFiles="log.vr.$LogDate-*_$HostName*.log"
./LogBackUp.sh $LogFiles && echo `date` "daily task: $LogFiles" >> /data/logs/logupload/logbackup.$LogDate.log

LogFiles="log.eagle.$LogDate-*_$HostName*.log"
./LogBackUp.sh $LogFiles && echo `date` "daily task: $LogFiles" >> /data/logs/logupload/logbackup.$LogDate.log