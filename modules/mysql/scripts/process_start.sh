#!/usr/bin/env bash
projectName="MoreTV_FrontPagePersonal"
scriptName=`basename $0`
server_pid="MoreTV_FrontPagePersonal.pid"
###定义脚本锁函数
function lock_script(){
    pid_file="/tmp/${scriptName}.pid"
    lockcount=0
    script_id=`echo $$`
    while [ $lockcount -le 3 ];do
        if [ -f "$pid_file" ];then
            process_id=`head -n 1 $pid_file`
            same_arguments=`ps $process_id|grep -w $scriptName|wc -l`
            if [ "$same_arguments" -ge 1 ];then
                write_exec_log "error" "The script is running......"
                sleep 30
                let lockcount++
            else
                break
            fi
        else
            break
        fi
    done

    ###进程pid写入文件
    echo $$ >$pid_file

    ###pid文件赋权
    chmod 666 "$pid_file"
}

lock_script


###查看进程状态
function status_process(){
    ###进程类型变量
    service_file="/tmp/$server_pid"
    service_id=`head -n 1 $service_file`
    same_arguments=`ps $service_id|grep -w $projectName|wc -l`
    if [ "$same_arguments" -ge 1 ];then
        echo  "The service is running......"
        exit 2
    else
        return 0
    fi
}


# 参数：topic bucket configpath groupid cassandraName
#status_process
status_process
cd /opt/ai/kafkaIO/shell
nohup java -XX:+UseParNewGC -XX:+UseConcMarkSweepGC -Djava.awt.headless=true -XX:CMSInitiatingOccupancyFraction=75 -XX:+UseCMSInitiatingOccupancyOnly -XX:+HeapDumpOnOutOfMemoryError -Xmx3g -Xms3g -cp ../jar/Kafka2Couchbase4Interest.jar com.moretv.consumer.couchbase.CouchbaseOffline10 MoreTV_FrontPagePersonal Moretv_InterestRecommend  ../conf/ucloudConfig.json interestGroupId1 interest 50000 6 > ../logs/MoreTV_InterestOptimizationOffline.log 2>&1 &
echo $! > /tmp/$server_pid