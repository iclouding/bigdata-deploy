#check write
hadoop fs -ls -t /tmp/test > c.log

#check read
cd restore
ls |wc -l   #数据量与ls -lt|head最大值
ls -lt|head