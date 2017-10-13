#!/bin/bash

#
# $1 dateStr , $2 listFile , $3 remoteListFile
#
send_file()
{
    dateStr=$1
    listFile=$2
    remoteListFile=$3

    cat $listFile > $remoteListFile
    ret="$?"
    if [ "x$ret"=="x0" ];then
        #触发上传
        chown spark:hadoop $remoteListFile
        su - spark -c "ssh spark@bigdata-appsvr-130-6 'nohup /opt/logupload/NginxLogUpload.sh $remoteListFile $dateStr >> /data/logs/logupload/NginxLogUpload.$dateStr.log 2>&1 &'"
        ret="$?"
        echo `date` "upload end[${ret}] for $listFile -> $remoteListFile"
        if [ "x$ret"=="x0" ];then
            rm $listFile
        fi
    else
        echo `date` "generate list file error[${ret}] for $listFile -> $remoteListFile"
    fi
}

#移动文件
#
# $1 dateStr , $2 timeStr , $3 listFile
#
move_file()
{
    dateStr=$1
    timeStr=$2
    listFile=$3
    > $listFile

    backupDir=/data/backups/nginx_log/$dateStr
    for file in `ls $logDir/*.log-${timeStr}*|grep -v "error.log-*"|grep -v "access.log-*"`
    do
        fileName=${file##*/}
        targetFile="$backupDir/$fileName"
        if [ -f "$targetFile" ]; then
            currTime=`date +%Y%m%d%H%M%S`
            targetFile="$targetFile-$currTime"
        fi
        mv -f $file $targetFile && echo `date` "mv file $file to $targetFile"
        echo "$targetFile" >> $listFile
    done
}

host=`hostname`
logDir=/data/logs/nginx

#移动目标文件
arr=("20170314 20170315 20170316 20170317 20170318 20170319")
for d in $arr
do
    echo "dateStr is $d"
    dateStr="$d"
    timeStr="${d}23"
    listFile=/tmp/nginx_log_$timeStr_$host.list
    remeteListFile="/data/backups/nginx_log/nginx_log_${timeStr}_${host}.list"
    move_file $dateStr $timeStr $listFile
    send_file $dateStr $listFile $remeteListFile
done




