#!/usr/bin/env bash
LogDate=$1
if [ -z "$LogDate" ]; then
    LogDate=`date -d '1 hour ago' +%Y-%m-%d`
fi
LogDateShort=`echo $LogDate|tr -d '-'`
LogcenterDir="/data/logs/logcenter/current"

echo `date` daily task $LogDate .......................

if [ ! -d "$LogcenterDir/$LogDateShort" ]; then
    mkdir -p $LogcenterDir/$LogDateShort
fi
mv -f $LogcenterDir/log.*.$LogDate-*.log.bz2 $LogcenterDir/$LogDateShort && \
    echo "move files $LogcenterDir/log.*.$LogDate-*.log.bz2 to $LogcenterDir/$LogDateShort"

