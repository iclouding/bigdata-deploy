#!/bin/bash

LOCALPATH=/data/backups/hdfs_temp/back_cron
REMOTEPATH=/backup/crontab

hadoop fs -put $LOCALPATH $REMOTEPATH
#su - spark -c "hadoop fs -put $LOCALPATH $REMOTEPATH"
