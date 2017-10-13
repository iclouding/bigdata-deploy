#!/bin/bash

dateStr=`date -d '-1 day' +%Y%m%d`
logDir=/data/logs/nginx

if [ -d $logDir/$dateStr ]; then
    echo $logDir/$dateStr exists,log maybe always rotated!!!
    exit 1
fi

mkdir -p $logDir/$dateStr

echo rename file $dateStr
for file in `ls $logDir/*.log|grep -v "*"`
do
    mv $file $file-$dateStr
done

echo reopen file
/opt/openresty/nginx/sbin/nginx -s reopen
sleep 1

echo move file $dateStr
for file in `ls $logDir/*.log|grep -v "*"`
do
    mv $file-$dateStr $logDir/$dateStr
done

