#!/usr/bin/env bash

LogFiles=$1
backupRoot=/data/backups
cd `dirname $0`
pwd=`pwd`
HostName=`hostname`
LogDate=`date -d '1 hour ago' +%Y-%m-%d`
LogTime=`date -d '1 hour ago' +%Y-%m-%d-%H`
LogcenterDir="/data/logs/logcenter/current"
backupDir="$backupRoot/logcenter"
taskLogFile="/data/logs/logupload/logbackup.$LogDate.log"

#从备份目录读取环境配置信息
if [ -f "$backupRoot/.profile" ]; then
    source $backupRoot/.profile
    echo "load profile from $backupRoot/.profile. backup_host=${backup_host},backup_user=${backup_user}" >> $taskLogFile
fi
backup_host=${backup_host:-bigdata-appsvr-130-6}
backup_user=${backup_user:-spark}

echo "start backup task. backup_host=${backup_host},backup_user=${backup_user}" >> $taskLogFile


#创建备份目录
if [ ! -d $backupDir ]; then
    mkdir -p $backupDir && echo `date` "mkdir $backupDir"
fi
if [ ! -d $backupDir ]; then
    echo `date` "[ERROR] :failure create dir $backupDir"
    exit 1
fi

if [ -n "$LogFiles" ]; then
    LogFiles=`echo $LogFiles|sed  s/"{hostname}"/"$HostName"/g`
else
    LogFiles="log.*.${LogTime}_${HostName}_*.log"
fi


echo `date` "copy start $LogcenterDir/$LogFiles" >> $taskLogFile
#rsync $LogcenterDir/$LogFiles ${backup_user}@${backup_host}:$LogcenterDir/ >> $taskLogFile
for file in `ls $LogcenterDir/$LogFiles`
do
    cp $file $backupDir/
done

ret="$?"
echo `date` "copy end[${ret}] for $LogFiles" >> $taskLogFile

su - ${backup_user} -c "ssh ${backup_user}@${backup_host} 'nohup $pwd/LogUpload.sh $LogFiles >> /data/logs/logupload/logupload.$LogDate.log 2>&1 &'"
ret="$?"
echo `date` "upload end[${ret}] for $LogFiles" >> $taskLogFile


