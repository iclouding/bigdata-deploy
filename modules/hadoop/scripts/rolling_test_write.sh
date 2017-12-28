#!/usr/bin/env bash

for ((i=1; i<=100000; i ++))
do
    filename="${i}.txt"
    echo "${i}" > ${filename}
    hadoop fs -put ${filename} /tmp/test
    rm ${filename}
    sleep 2s
done

#hadoop@bigdev-cmpt-1
# cd /home/hadoop/test;nohup sh rolling_test_write.sh >a.log 2>&1 &