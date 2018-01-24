#!/usr/bin/env bash

for ((i=1; i<=100000; i ++))
do
    filename="hbase_import"
    echo "put 'check_hadoop_rolling_write2','${i}','count','${i}'" > ${filename}
    sleep 2s
    /opt/hbase/bin/hbase shell ${filename}
done

#hadoop@bigtest-appsvr-129-1
# /home/hadoop/check_script
# nohup sh rolling_test_hbase_write.sh >hbase.log 2>&1 &

# create 'check_hadoop_rolling_write2','count'
# put 'check_hadoop_rolling_write2','0','count','0'
# scan 'check_hadoop_rolling_write2'


#check Database integrity
#count 'check_hadoop_rolling_write2'
