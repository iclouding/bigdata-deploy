#!/usr/bin/env bash

#use hadoop user to delete KYLIN application log

HADOOP_HOME=/opt/hadoop
LOG_PREFIX=/tmp/logs/hadoop
hdfsfiles=" "
count=0
for filename in `${HADOOP_HOME}/bin/yarn application -appStates FINISHED,FAILED,KILLED -list | grep Kylin_|awk '{print $1}' `
do
	        hdfsfile=${LOG_PREFIX}/${filename};
	        hdfsfiles=$hdfsfiles" "$hdfsfile;
            if [ ${count} -eq 10 ]; then
                echo "needrm $hdfsfiles"
                $HADOOP_HOME/bin/hadoop fs -rm -r ${hdfsfile}
                hdfsfiles=" ";
                count=0
            fi
            let count=count+1;
done



