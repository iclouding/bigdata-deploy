#!/usr/bin/env bash
pid=$$
logListFile=$1
logDirDate=$2
logDir="/data/backups/nginx_log"
uploadResult="success"

moretv2xHdfsPath="/log/moretv2x/rawlog"
moretv2xFilePrefix="/log.moretv.log"

mtvkidsHdfsPath="/log/mtvkids/rawlog"
mtvkidsFilePrefix="/mtvkidslog.moretv.log"

activityHdfsPath="/log/activity/rawlog"
activityFilePrefix="/activity.moretv.log"

metisHdfsPath="/log/metis/rawlog"
metisFilePrefix="/metislog.moretv.log"

weixinHdfsPath="/log/weixin/rawlog"
weixinFilePrefix="/weixinlog.moretv.log"

danmuHdfsPath="/log/danmu/rawlog"
danmuFilePrefix="/danmulog.moretv.log"

j8ilnoi7HdfsPath="/log/boikgpokn78sb95kjhfrendoj8ilnoi7/rawlog"
j8ilnoi7FilePrefix="/boikgpokn78sb95kjhfrendoj8ilnoi7.log"

defaultHdfsPath="/log/boikgpokn78sb95k0000000000000000/rawlog"
defaultFilePrefix="/boikgpokn78sb95k0000000000000000.log"

oepkseljnHdfsPath="/log/boikgpokn78sb95kjhfrendoepkseljn/rawlog"
oepkseljnFilePrefix="/boikgpokn78sb95kjhfrendoepkseljn.log"

bgjgjolqHdfsPath="/log/boikgpokn78sb95kjhfrendobgjgjolq/rawlog"
bgjgjolqFilePrefix="/boikgpokn78sb95kjhfrendobgjgjolq.log"

icggqhbkepkseljnHdfsPath="/log/boikgpokn78sb95kicggqhbkepkseljn/rawlog"
icggqhbkepkseljnFilePrefix="/boikgpokn78sb95kicggqhbkepkseljn.log"

jhfrendojtihcg26HdfsPath="/log/boikgpokn78sb95kjhfrendojtihcg26/rawlog"
jhfrendojtihcg26FilePrefix="/boikgpokn78sb95kjhfrendojtihcg26.log"

echo `date` task start $pid .......................

function upload2hdfs(){
    hdfsPath=$1
    filePrefix=$2

    /opt/hadoop/bin/hadoop fs -mkdir -p $hdfsPath/$logDirDate
    echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo -e "\033[34m[`date`] start execute ${filePrefix} \033[0m"
    set -x
    /opt/hadoop/bin/hadoop fs -put -f `cat $logListFile | grep $filePrefix` $hdfsPath/$logDirDate/
    result=$?
    set +x
    if [ $result -eq 0 ];then
        echo -e "\033[32m[`date`] end   execute $filePrefix \033[0m"
    else
        uploadResult="failure"
        echo -e "\033[31m[`date`] error execute $filePrefix \033[0m"
    fi

}

function uploadRawLog2hdfs(){
    hdfsPathPrefix=$1
    filePrefix=$2

    keyDayHour=`grep -o -E "\-[0-9]{10}\-" $logListFile|head -1`
    keyDay=${keyDayHour:1:8}
    keyHour=${keyDayHour:9:2}

    hdfsPath=$hdfsPathPrefix/key_day=$keyDay/key_hour=$keyHour

    /opt/hadoop/bin/hadoop fs -mkdir -p $hdfsPath
    echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo -e "\033[34m[`date`] start execute ${filePrefix} \033[0m"
    set -x
    /opt/hadoop/bin/hadoop fs -put -f `cat $logListFile | grep $filePrefix` $hdfsPath
    result=$?
    set +x
    if [ $result -eq 0 ];then
        /opt/hive/bin/hive -e "alter table ods_origin.log_raw add partition(key_day='$keyDay',key_hour='$keyHour') location '$hdfsPath'"
        echo -e "\033[32m[`date`] end   execute $filePrefix \033[0m"
    else
        uploadResult="failure"
        echo -e "\033[31m[`date`] error execute $filePrefix \033[0m"
    fi

}

upload2hdfs $moretv2xHdfsPath $moretv2xFilePrefix
upload2hdfs $mtvkidsHdfsPath $mtvkidsFilePrefix
upload2hdfs $activityHdfsPath $activityFilePrefix
upload2hdfs $metisHdfsPath $metisFilePrefix
upload2hdfs $weixinHdfsPath $weixinFilePrefix
upload2hdfs $danmuHdfsPath $danmuFilePrefix
upload2hdfs $j8ilnoi7HdfsPath $j8ilnoi7FilePrefix
upload2hdfs $defaultHdfsPath $defaultFilePrefix
upload2hdfs $oepkseljnHdfsPath $oepkseljnFilePrefix
upload2hdfs $bgjgjolqHdfsPath $bgjgjolqFilePrefix
upload2hdfs $icggqhbkepkseljnHdfsPath $icggqhbkepkseljnFilePrefix
upload2hdfs $jhfrendojtihcg26HdfsPath $jhfrendojtihcg26FilePrefix
uploadRawLog2hdfs "/data_warehouse/ods_origin.db/log_raw" "log"

if [ $uploadResult = "success" ]; then
    echo "[`date`]" cat $logListFile
    cat $logListFile
    rm -f $logListFile
    echo "[`date`]" rm -f $logListFile
fi

echo `date` task end   $pid ......................
