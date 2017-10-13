--ddl--

CREATE EXTERNAL TABLE `ods.t_log_cdn_mediags`(
  `time_localtime` string,
  `server_addr` string,
  `src_request_uri` string,
  `real_client_addr` string,
  `remote_port` string,
  `real_x_forworded` string,
  `real_domain` string,
  `request_method` string,
  `status` string,
  `bytes_sent` string,
  `cache_state` string,
  `real_uri` string,
  `store_uri` string,
  `request_is_normal_closed` string,
  `http_range` string,
  `http_user_agent` string,
  `http_referer` string,
  `http_cookie` string,
  `step_code` string,
  `request_time_msec` string,
  `server_protocol` string,
  `real_local_ip_string` string,
  `body_bytes_sent` string,
  `content_length` string,
  `upstream_response_time` string,
  `req_headers` string,
  `resp_headers` string,
  `extra_1` string,
  `extra_2` string,
  `connection` string,
  `remote_user` string,
  `upstream_addr` string,
  `upstream_status` string,
  `upstream_cache_status` string,
  `server_type` string,
  `cache_state_in_gsvc` string,
  `billing_extra` string,
  `billing_type` string,
  `msec` string,
  `billing_domain` string)
PARTITIONED BY (
  `key_time` string,
  `key_host` string)
ROW FORMAT SERDE
  'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'field.delim'='\t',
  'serialization.format'='\t')
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  'hdfs://hans/user/hive/warehouse/ods.db/t_log_cdn_mediags'
  ;

drop view if exists ods.v_log_cdn_mediags;
create view ods.v_log_cdn_mediags as
    select split(`a`.`real_uri`,'/')[3] as `sid`,`a`.*
    from `ods`.`t_log_cdn_mediags` `a`
    ;

#统计
explain
select a.host,a.day,a.sid,a.title,a.total_bytes
    ,a.r
    ,from_unixtime(unix_timestamp(),'yyyy-MM-dd HH:mm:ss') as create_time
from (
    select a.*,dense_rank() over(order by a.total_bytes desc) as r
    from (
        select a.key_host as host,a.key_time as day,a.sid,b.title
            ,sum(cast(a.bytes_sent as bigint)) as total_bytes
        from ods.v_log_cdn_mediags a
            inner join dw_dimensions.dim_medusa_program b on b.sid=a.sid
        where nvl(a.bytes_sent,'')!='' and key_time='20170411'
        group by a.key_host,a.key_time,a.sid,b.title
    ) a
) a
where a.r<=200
;

--DROP TABLE bi.cdn_sendbytes_statistics;
CREATE TABLE bi.cdn_sendbytes_statistics (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `day` varchar(20) NOT NULL,
  `host` varchar(50) DEFAULT NULL,
  `sid` varchar(50) NOT NULL,
  `title` varchar(100) DEFAULT NULL,
  `total_bytes` bigint NOT NULL,
  `host_total_bytes` bigint NOT NULL,
  `ratio` float NOT NULL,
  `rank` int DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ;



----test case-----------
taskTime=`date "+%Y-%m-%d %H:%M:%S"`
logTime=20170416
host=mediags.moguv.com
hdfsDir=/tmp/cdn_statistic/$host/$logTime
jdbcUrl="jdbc:mysql://bigdata-appsvr-130-1:3306/bi?useUnicode=true&characterEncoding=utf-8&autoReconnect=true"
jdbcUser=bi
jdbcPassword="mlw321@moretv"

hive -e "
set tez.am.resource.memory.mb=4096;
set hive.tez.container.size=4096;
insert overwrite directory '$hdfsDir'
    select a.day,a.host,a.sid,a.title,a.total_bytes
        ,a.r as rank
        ,'${taskTime}' as create_time
    from (
        select a.*,dense_rank() over(order by a.total_bytes desc) as r
        from (
            select a.key_host as host
                ,a.key_time as day
                ,a.sid,b.title
                ,sum(cast(a.bytes_sent as bigint)) as total_bytes
            from ods.v_log_cdn_mediags a
                inner join dw_dimensions.dim_medusa_program b on b.sid=a.sid
            where nvl(a.bytes_sent,'')!='' and key_time='$logTime' and a.key_host='$host'
            group by a.key_host,a.key_time,a.sid,b.title
        ) a
    ) a
where a.r<=200
"


/opt/sqoop/bin/sqoop-export --connect $jdbcUrl --username $jdbcUser --password $jdbcPassword \
    --table cdn_sendbytes_statistics  --export-dir $hdfsDir  \
    --fields-terminated-by '\001' --input-lines-terminated-by '\n'  \
    --input-null-string '\\N' --input-null-non-string '\\N' \
    --columns "day,host,sid,title,total_bytes,rank,create_time"


/opt/sqoop/bin/sqoop eval --connect $jdbcUrl --username $jdbcUser --password $jdbcPassword \
    -e "delete from cdn_sendbytes_statistics where day='20170410' and create_time!='2017-04-17 16:03:45'"


------


--azkaban发布包,工程: ods_etl_cdn_log

#压缩
rm -f ods_etl_cdn_log.zip
zip ods_etl_cdn_log.zip azkaban/*/*
unzip -l ods_etl_cdn_log.zip

#解压
unzip ods_etl_cdn_log.zip -d /tmp