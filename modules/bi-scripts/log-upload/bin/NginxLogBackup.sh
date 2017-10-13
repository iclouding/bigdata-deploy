#!/bin/bash

backupRoot=/data/backups

#从备份目录读取环境配置信息
if [ -f "$backupRoot/.profile" ]; then
    source $backupRoot/.profile
    echo "load profile from $backupRoot/.profile. backup_host=${backup_host},backup_user=${backup_user}"
fi

backup_host=${backup_host:-bigdata-appsvr-130-6}
backup_user=${backup_user:-spark}

echo "start backup task. backup_host=${backup_host},backup_user=${backup_user}"

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
        su - ${backup_user} -c "ssh ${backup_user}@${backup_host} 'nohup /opt/logupload/NginxLogUpload.sh $remoteListFile $dateStr >> /data/logs/logupload/NginxLogUpload.$dateStr.log 2>&1 &'"
        ret="$?"
        echo `date` "upload end[${ret}] for $listFile -> $remoteListFile"
        if [ "x$ret"=="x0" ];then
            rm $listFile
        fi
    else
        echo `date` "generate list file error[${ret}] for $listFile -> $remoteListFile"
    fi
}

host=`hostname`
dateStr=`date -d '-1 hour' +%Y%m%d`
timeStr=`date -d '-1 hour' +%Y%m%d%H`
logDir=/data/logs/nginx
backupDir=$backupRoot/nginx_log/$dateStr

#创建备份日期目录
if [ ! -d $backupDir ]; then
    mkdir -p $backupDir && echo `date` "mkdir $backupDir"
fi
if [ ! -d $backupDir ]; then
    echo `date` "[ERROR] :failure create dir $backupDir"
    exit 1
fi

#重命名当前文件
for file in `ls $logDir/*.log|grep -v "*"|grep -v "error.log"|grep -v "access.log" `
do
    targetFile="$file-$timeStr-$host"
    if [ -f "$targetFile" ]; then
        currTime=`date +%Y%m%d%H%M%S`
        targetFile="$file-$currTime-$host"
    fi
    mv -f $file $targetFile && echo `date` "rename $file to $targetFile"
done

#nginx文件重开
/opt/openresty/nginx/sbin/nginx -s reopen && echo `date` "echo nginx reopen file" && sleep 1


#移动除当前时间外的所有滚动文件，这样做是为其他应用（如filebeat）保留充分的处理时间
listFile=/tmp/nginx_log_$timeStr_$host.list
> $listFile
for file in `ls $logDir/*.log-$dateStr*|grep -v "*"|grep -v $timeStr|grep -v "error.log-*"|grep -v "access.log-*"`
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

remeteListFile="/data/backups/nginx_log/nginx_log_${timeStr}_${host}.list"
send_file $dateStr $listFile $remeteListFile


#####################前一天的遗留日志##############################
dateStr=`date -d '-1 day' +%Y%m%d`
fileCount=`ls $logDir/*.log-$dateStr*|grep -v "*"|wc -l`
if [ "x$fileCount" == "x0" ]; then
    exit 0
fi

backupDir=/data/backups/nginx_log/$dateStr
listFile=/tmp/nginx_log_$dateStr_$host.list
> $listFile
for file in `ls $logDir/*.log-$dateStr*|grep -v "*"|grep -v "error.log-*"|grep -v "access.log-*"`
do
    fileName=${file##*/}
    targetFile="$backupDir/$fileName"
    if [ -f "$targetFile" ]; then
        currTime=`date +%Y%m%d-%H%M%S`
        targetFile="$targetFile-$currTime"
    fi
    mv -f $file $targetFile && echo `date` "mv file $file to $targetFile"
    echo "$targetFile" >> $listFile
done

remeteListFile="/data/backups/nginx_log/nginx_log_${dateStr}_${host}.list"
send_file $dateStr $listFile $remeteListFile

#清除3天前的list文件
t0=`date -d '0 day' +%Y%m%d`
t1=`date -d '-1 day' +%Y%m%d`
removed=`ls /data/backups/nginx_log/nginx_log_*.list|grep -v nginx_log_$t0|grep -v nginx_log_$t1`
echo "removed file: $removed"
rm -f $removed
