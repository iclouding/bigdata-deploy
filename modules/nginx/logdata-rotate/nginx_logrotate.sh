#!/bin/bash

host=`hostname`
dateStr=`date -d '-1 hour' +%Y%m%d`
timeStr=`date -d '-1 hour' +%Y%m%d%H`
logDir=/data/logs/nginx
backupDir=/data/backups/nginx_log/$host

#创建备份日期目录
if [ ! -d $backupDir/$dateStr ]; then
    mkdir -p $backupDir/$dateStr && echo `date` "mkdir $backupDir/$dateStr"
fi
if [ ! -d $backupDir/$dateStr ]; then
    echo `date` "[ERROR] :failure create dir $backupDir/$dateStr"
    exit 1
fi

#重命名当前文件
for file in `ls $logDir/*.log|grep -v "*"`
do
    mv -f $file $file-$timeStr && echo `date` "rename $file to $file-$timeStr"
done

#nginx文件重开
/opt/openresty/nginx/sbin/nginx -s reopen && echo `date` "echo nginx reopen file" && sleep 1


#移动除当前时间外的所有滚动文件，这样做是为其他应用（如filebeat）保留充分的处理时间
for file in `ls $logDir/*.log-$dateStr*|grep -v "*"|grep -v $timeStr`
do
    mv -f $file $backupDir/$dateStr && echo `date` "mv file $file to $backupDir/$dateStr"
done

#前一天的遗留日志
dateStr=`date -d '-1 day' +%Y%m%d`
mv -f $logDir/*.log-$dateStr* $backupDir/$dateStr && echo `date` "mv file $logDir/*.log-$dateStr* to $backupDir/$dateStr"

