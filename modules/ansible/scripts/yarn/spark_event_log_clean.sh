#!/bin/bash

day=`date +%s`
HADOOP_HOME=/opt/hadoop
hdfsfiles=" "
count=1
for filename in `$HADOOP_HOME/bin/hadoop fs -ls /spark-log/spark-events | awk '{print $6","$8}' `
do
    if [ ${#filename} -gt 20 ]; then
	    fileDate=${filename%,*}
	    fileDate=`date -d "$fileDate" +%s`
	    timeDiff=`expr $day - $fileDate`
	    if [ $timeDiff -lt 604800 ]; then
	        echo "reserve $filename";
	    else
	        hdfsfile=${filename#*,};
	        hdfsfiles=$hdfsfiles" "$hdfsfile;
	    fi
            if [ $count -eq 100 -a ${#hdfsfiles} -gt 10 ]; then
                $HADOOP_HOME/bin/hadoop fs -rm -r $hdfsfiles;
                hdfsfiles=" ";
                let count=1;
            fi
            let count=count+1;
	fi
done

if [ ${#hdfsfiles} -gt 10 ]; then
    $HADOOP_HOME/bin/hadoop fs -rm -r $hdfsfiles;
fi
