#!/usr/bin/env bash
pid=$$
localDirDate=`date -d '-1 day' +%y%m%d`
hdfsDirDate=`date -d '-1 day' +%Y%m%d`
localDir="/data/backups/api_nginx_log/moretv_recommend/$localDirDate"
hdfsDir="/log/api_nginx_log_moretv_recommend/$hdfsDirDate"
uploadResult="success"

echo `date` task start $pid .......................

/opt/hadoop/bin/hadoop fs -mkdir -p $hdfsDir

for file in `cd $localDir && ls `
do
  filename=${file:1}
  /opt/hadoop/bin/hadoop fs -put -f $localDir/$file $hdfsDir/$filename
done


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


#if [ $uploadResult = "success" ]; then
#    echo "[`date`]" cat $logListFile
#    cat $logListFile
#    rm -f $logListFile
#    echo "[`date`]" rm -f $logListFile
#fi

echo `date` task end   $pid ......................
