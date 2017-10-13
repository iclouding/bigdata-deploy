#!/usr/bin/env bash
pid=$$
LogFiles="$1"
backupRoot=/data/backups

#LogcenterDir="/data/logs/logcenter/current"
LogcenterDir="$backupRoot/logcenter"
ListPrefix=`echo $LogFiles|tr -s '*' 'X'`

echo `date` $LogFiles task start $pid .......................

rm  /tmp/$ListPrefix.*.list

files=`ls $LogcenterDir/${LogFiles}`
if [ -z "$files" ]; then
    echo $LogFiles no files
    exit 1
fi

c=`ps -ef|grep -v $pid|grep LogUpload|grep -v grep|grep "$LogFiles"|wc -l`
if [ "x$c" != "x0" ];then
    echo $LogFiles always uploading,exit 1
    echo `ps -ef|grep -v $pid|grep LogUpload|grep -v grep|grep "$LogFiles"`
    exit 1
fi

#log files
echo `date` "processing files $LogcenterDir/${LogFiles}"
for file in $files
do
    logType=$(expr "$file" : ".*/log[.]\(.*\)[.][0-9]\{4\}.*")
    if [ "$logType" == "helios" ]; then
        logType="whaley"
    fi

    if [ -n "$logType" ]; then
        echo "$file" >> /tmp/$ListPrefix.logupload.$logType.list && \
        echo `date` "add log $file to /tmp/$ListPrefix.logupload.$logType.list "
    else
        echo invalid log file $file
    fi

done

echo `date` uploading file

for listFile in `ls /tmp/$ListPrefix.logupload.*.list`
do
    logType=$( expr "$listFile" : ".*logupload[.]\(.*\)[.]list")
    #每日一个清单文件
    rm -f /tmp/$ListPrefix.logupload.$logType.*.list
    for logFile in `cat $listFile`
    do
        logDate=`echo $(expr "$logFile" : '.*log[.].*[.]\([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}\)-.*') | tr -d "-"`
        if [ -z $logDate ]; then
            logDate="NULL"
        fi
        echo $logFile >> /tmp/$ListPrefix.date.$logType.$logDate.list
        echo "add $logFile to /tmp/$ListPrefix.date.$logType.$logDate.list"
    done

    #逐个处理清单文件
    for dateFile in `ls /tmp/$ListPrefix.date.$logType.*.list`
    do
        logDate=$( expr "$dateFile" : ".*date[.]$logType[.]\(.*\)[.]list")
        if [ "$logDate" == "NULL" ]; then
            logDate=""
        fi
        /opt/hadoop/bin/hadoop fs -mkdir -p /log/$logType/rawlog/$logDate
        echo `date` "upload $logType files $dateFile to /log/$logType/rawlog/$logDate " `cat $dateFile|wc -l` && \
            /opt/hadoop/bin/hadoop fs -put -f `cat $dateFile` /log/$logType/rawlog/$logDate

        if [ ! -d "$LogcenterDir/$logDate" ]; then
            mkdir -p $LogcenterDir/$logDate
        fi
        mv -f `cat $dateFile`  "$LogcenterDir/$logDate" && rm -f $dateFile && echo "move file in $dateFile to $LogcenterDir/$logDate"

        echo `date` "process file $dateFile"
    done

    rm -f $listFile
done

echo `date` $LogFiles task end $pid ......................



