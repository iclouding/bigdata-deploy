#!/bin/bash

cd `dirname $0`

source /etc/profile
source ~/.bash_profile

task=$1
mainClass="com.whaley.mysql2redis.Main"

case "$task" in
    mysql2redis_tvservice.mtv_channel-1)
        ./submit.sh $mainClass --app_name=$task --flag=1 --dbkey=jdbc-helios-slave-tvservice-program --rediskey=redis-whaley-bi --redisdb=1 --table=mtv_channel --col=sid,station
    ;;
    mysql2redis_tvservice.mtv_channel-0)
        ./submit.sh $mainClass --app_name=$task --flag=0 --dbkey=jdbc-helios-slave-tvservice-program --rediskey=redis-whaley-bi --redisdb=1 --table=mtv_channel --col=sid,station
    ;;
    mysql2redis_tvservice.mtv_subject-1)
        ./submit.sh $mainClass --app_name=$task --flag=1 --dbkey=jdbc-helios-slave-tvservice-program --rediskey=redis-whaley-bi --redisdb=0 --table=mtv_subject --col=code,name
    ;;
    mysql2redis_mtv_cms.sailfish_sport_match-1)
        ./submit.sh $mainClass --app_name=$task --flag=1 --dbkey=jdbc-moretv-slave-mtv_cms --rediskey=redis-whaley-bi --redisdb=2 --table=sailfish_sport_match --col=sid,title
    ;;
    mysql2redis_mtv_cms.sailfish_sport_match-0)
        ./submit.sh $mainClass --app_name=$task --flag=0 --dbkey=jdbc-moretv-slave-mtv_cms --rediskey=redis-whaley-bi --redisdb=2 --table=sailfish_sport_match --col=sid,title
    ;;
    mysql2redis_mtv_cms.mtv_basecontent-1)
        ./submit.sh $mainClass --app_name=$task --flag=1 --dbkey=jdbc-moretv-slave-mtv_cms --rediskey=redis-whaley-bi --redisdb=3 --table=mtv_basecontent --col=sid,display_name,content_type,duration,tags,information,douban_tags,cast
    ;;
    mysql2redis_mtv_cms.mtv_basecontent-0)
        ./submit.sh $mainClass --app_name=$task --flag=0 --dbkey=jdbc-moretv-slave-mtv_cms --rediskey=redis-whaley-bi --redisdb=3 --table=mtv_basecontent --col=sid,display_name,content_type,duration,tags,information,douban_tags,cast
    ;;
    mysql2redis-tvservice_helio.mtv_program-1)
        ./submit.sh $mainClass --app_name=$task --flag=1 --dbkey=jdbc-helios-slave-tvservice-program --rediskey=redis-whaley-ai --redisdb=0 --table=mtv_program --colAlias=update_time:updateTime --col=sid,type,status,title,updateTime,duration,tags,area,epstitle,episodeCount,videoType,contentType,score,episode,doubanId,areaCode,createTime,quarter_id,quarter,supply_type,videoLengthType
    ;;
    mysql2redis-tvservice_helio.mtv_program-0)
        ./submit.sh $mainClass --app_name=$task --flag=0 --dbkey=jdbc-helios-slave-tvservice-program --rediskey=redis-whaley-ai --redisdb=0 --table=mtv_program --colAlias=update_time:updateTime --col=sid,type,status,title,updateTime,duration,tags,area,epstitle,episodeCount,videoType,contentType,score,episode,doubanId,areaCode,createTime,quarter_id,quarter,supply_type,videoLengthType
    ;;
    mysql2redis-tvservice_mtv.mtv_program-1)
        ./submit.sh $mainClass --app_name=$task --flag=1 --dbkey=jdbc-moretv-slave-tvservice-program --rediskey=redis-whaley-bi --redisdb=6 --table=mtv_program --colAlias=update_time:updateTime --fieldPrefix=item_ --col=id,type,parentid,sid,title,status,year,videoType,contentType,updatetime,host,actor,director,cast,guest,tags,area,station,score,rank,duration
    ;;
    mysql2redis-tvservice_mtv.mtv_program-0)
        ./submit.sh $mainClass --app_name=$task --flag=0 --dbkey=jdbc-moretv-slave-tvservice-program --rediskey=redis-whaley-bi --redisdb=6 --table=mtv_program --colAlias=update_time:updateTime --fieldPrefix=item_ --col=id,type,parentid,sid,title,status,year,videoType,contentType,updatetime,host,actor,director,cast,guest,tags,area,station,score,rank,duration
    ;;
    mysql2redis-tvservice_helio_forai.mtv_program-1)
        ./submit.sh $mainClass --app_name=$task --flag=1 --dbkey=jdbc-helios-slave-tvservice-program --rediskey=redis-whaley-ai --redisdb=20 --table=mtv_program --colAlias=update_time:updateTime --fieldAsArray=true --col=sid,type,status,title,updateTime,duration,tags,area,epstitle,episodeCount,videoType,contentType,score,episode,doubanId,areaCode,createTime,quarter_id,quarter,supply_type,videoLengthType
    ;;
    mysql2redis-tvservice_helio_forai.mtv_program-0)
        ./submit.sh $mainClass --app_name=$task --flag=0 --dbkey=jdbc-helios-slave-tvservice-program --rediskey=redis-whaley-ai --redisdb=20 --table=mtv_program --colAlias=update_time:updateTime --fieldAsArray=true --col=sid,type,status,title,updateTime,duration,tags,area,epstitle,episodeCount,videoType,contentType,score,episode,doubanId,areaCode,createTime,quarter_id,quarter,supply_type,videoLengthType
    ;;
    mysql2redis-tvservice_mtv_forai.mtv_program-1)
        ./submit.sh $mainClass --app_name=$task --flag=1 --dbkey=jdbc-moretv-slave-tvservice-program --rediskey=redis-whaley-bi --redisdb=20 --table=mtv_program --colAlias=update_time:updateTime --fieldAsArray=true --fieldPrefix=item_ --col=id,type,parentid,sid,title,status,year,videoType,contentType,updatetime,host,actor,director,cast,guest,tags,area,station,score,rank,duration
    ;;
    mysql2redis-tvservice_mtv_forai.mtv_program-0)
        ./submit.sh $mainClass --app_name=$task --flag=0 --dbkey=jdbc-moretv-slave-tvservice-program --rediskey=redis-whaley-bi --redisdb=20 --table=mtv_program --colAlias=update_time:updateTime --fieldAsArray=true --fieldPrefix=item_ --col=id,type,parentid,sid,title,status,year,videoType,contentType,updatetime,host,actor,director,cast,guest,tags,area,station,score,rank,duration
    ;;
    *)
        echo invalid task $task
    ;;
esac