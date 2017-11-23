#!/bin/bash

####################################################################################
#
# sh ./process_cdn_statistic.sh --host=mediags.moguv.com --logTime=20170411 --offset=1 --jdbcUrl=${jdbcUrl} --jdbcUser=${jdbcUser} --jdbcPassword=${jdbcPassword}
#
####################################################################################
node=`hostname`
echo `date` "task started at $node"

cd `dirname $0`
pwd=`pwd`
source $pwd/envFn.sh

export debug=1
load_args $*

###jdbc######
if [ -z "$jdbcUrl" ]; then
    echo `date` "jdbcUrl is empty"
    exit 1
fi

if [ -z "$jdbcUser" ]; then
    echo `date` "jdbcUser is empty"
    exit 1
fi

###cdn########
if [ -z "$jdbcPassword" ]; then
    echo `date` "jdbcPassword is empty"
    exit 1
fi

if [ -z "$host" ]; then
    echo `date` "host is empty"
    exit 1
fi

if [ -z "$logTime" ]; then
    logTime=`date -d '1 day' +%Y%m%d`
fi

if [ -n "${offset}" ] && [ -n "${logTime}" ]; then
    logTime=`date -d "-$offset days "$logTime +%Y%m%d`
fi

#代码保护,去除空格,以避免错误地址传递导致错误删除的风险
hdfsDir=${outDir:-/tmp/cdn_statistic}/$host/$logTime
taskTime=`date "+%Y-%m-%d %H:%M:%S"`
echo `date` "statistic started."

if [ -z "$hdfsDir" ]; then
    echo `date` "hdfsDir is empty."
    exit 1
fi

microsoft_host='media-wr'
microsoft_host2='media2-wr'
table_name=""
if [[ $host == *$microsoft_host* ]] || [[ $host == *$microsoft_host2* ]]
then
  table_name="ods.v_log_microsoft_cdn_mediags"
  hive -e "
alter table ods.t_log_microsoft_cdn_mediags add if not exists partition(key_time='${logTime}',key_host='${host}')
location '/log/cdn/${logTime}/${host}';
"
else
  table_name="ods.v_log_cdn_mediags"
fi

set -x
hive -e "
set tez.am.resource.memory.mb=6144;
set hive.tez.container.size=6144;
set fs.hdfs.impl.disable.cache=true;

create table if not exists ods.tmp_cdn_mediags(sid string,total_bytes bigint)
partitioned by(key_host string,key_time string);

insert overwrite table ods.tmp_cdn_mediags partition(key_host='$host',key_time='$logTime')
    select a.sid,sum(cast(a.bytes_sent as bigint)) as total_bytes
    from ${table_name} a
    where nvl(a.bytes_sent,'')!='' and key_time='$logTime' and a.key_host='$host'
    group by a.key_host,a.key_time,a.sid
    order by total_bytes desc
    limit 200
    ;
"
ret=$?
if [ "$ret" != "0" ]; then
    echo `date` "failured to generate statistci data to tmp_cdn_mediags. ret=$ret"
    exit 1
fi

hive -e "
set tez.am.resource.memory.mb=6144;
set hive.tez.container.size=6144;
set fs.hdfs.impl.disable.cache=false;

insert overwrite directory '$hdfsDir'
    select a.day,a.host
        ,a.sid,a.title,a.total_bytes
        ,a.r as rank
        ,a.total_bytes/a.host_total_bytes as ratio
        ,a.host_total_bytes
        ,'${taskTime}' as create_time
    from (
        select a.*
            ,dense_rank() over(order by a.total_bytes desc) as r
            ,sum(total_bytes) over(partition by day,host)  as host_total_bytes
        from (
            select a.key_host as host,a.key_time as day
                ,a.sid,b.title,a.total_bytes
            from ods.tmp_cdn_mediags a
                inner join dw_dimensions.dim_medusa_program b on b.sid=a.sid
            where a.key_time='$logTime' and a.key_host='$host'
        ) a
    ) a
    ;
"
ret=$?
if [ "$ret" != "0" ]; then
    echo `date` "failured to generate statistci data to $hdfsDir. ret=$ret"
    exit 1
fi

set +x
echo `date` "statistic completed."

sqoop_home=${sqoop_home:-/opt/sqoop}
#export data
${sqoop_home}/bin/sqoop-export --connect $jdbcUrl --username $jdbcUser --password $jdbcPassword \
    --table cdn_sendbytes_statistics  --export-dir $hdfsDir  \
    --fields-terminated-by '\001' --input-lines-terminated-by '\n'  \
    --input-null-string '\\N' --input-null-non-string '\\N' \
    --columns "day,host,sid,title,total_bytes,rank,ratio,host_total_bytes,create_time"

ret=$?
if [ "$ret" != "0" ]; then
    echo `date` "failured to export statistci data. ret=$ret"
    exit 1
fi

#delete old data
${sqoop_home}/bin/sqoop eval --connect $jdbcUrl --username $jdbcUser --password $jdbcPassword \
    -e "delete from cdn_sendbytes_statistics where host='$host' and day='$logTime' and create_time!='$taskTime'"

ret=$?
if [ "$ret" != "0" ]; then
    echo `date` "failured to delete old statistci data for [$logTime,$taskTime].ret=$ret"
    exit 1
fi

#清理
hadoop fs -rm -r -f $hdfsDir
echo `date` "clean dir $hdfsDir"


