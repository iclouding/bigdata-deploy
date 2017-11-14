#!/bin/bash

####################################################################################
#
# sh ./process_gaoshen_cdn.sh --host=mediags.moguv.com --logTime=20170410 --offset=1
#
####################################################################################
node=`hostname`
echo `date` "task started at $node"


cd `dirname $0`
source envFn.sh

load_args $*

if [ -z "$host" ]; then
    echo `date` "host is empty"
fi

if [ -z "$logTime" ]; then
    logTime=`date -d '1 day' +%Y%m%d`
fi

if [ -n "${offset}" ] && [ -n "${logTime}" ]; then
    logTime=`date -d "-$offset days "$logTime +%Y%m%d`
fi

outDir=${outDir:-/tmp}
filePath="${outDir}/${host}_${logTime}.gz"

if [ -f "$filePath" ]; then
    echo `date` "rm old file $filePath"
    rm -f $filePath
fi

echo `date` "start get file $filePath"
python ./get_gaoshen_cdn.py -v $host -d $logTime -o  $outDir
ret=$?
if [ ! -f "$filePath" ] || [ "$ret" != "0" ]; then
    echo `date` "failured to get file $filePath, ret:$ret"
    exit 1
fi

#最小不能小于100K,否则认为是无效文件
#count=`wc -c $filePath|awk '{print $1}'`
#ret=$?
#if [ $count -lt 102400 ]; then
#    echo `date` "$filePath is too small. size=$count";
#    exit 1
#fi
#echo `date` "end get file. size=$count"

hdfsDir=/log/cdn/$logTime/$host/
hadoop fs -mkdir -p $hdfsDir
hadoop fs -put -f $filePath $hdfsDir

ret=$?
if [ "$ret" != "0" ]; then
    echo `date` "failured to upload file $filePath, ret:$ret"
    exit 1
fi
echo `date` "upload file: $filePath -> $hdfsDir"

hive -e "
alter table ods.t_log_cdn_mediags drop partition(key_time='$logTime',key_host='$host');
alter table ods.t_log_cdn_mediags add partition(key_time='$logTime',key_host='$host')
location '/log/cdn/$logTime/$host';
"

