#!/usr/bin/env bash

for ((i=1; i<=100000; i ++))
do
    filename="/tmp/test/${i}.txt"
    hadoop fs -get ${filename} restore/
    sleep 5s
done

#hadoop@bigdev-cmpt-1
# cd /home/hadoop/test;nohup sh rolling_test_read.sh >b.log 2>&1 &