#!/usr/bin/env bash

namenode_dir="/data/hdfs/name"
journalnode_dir="/data/hdfs/journal"
backup_dir="/data/hdfs/backup"
backup_date=`date '+%Y%m%d%H%M%S'`
echo `date` "start backup namenode data dir..."
mkdir -p $backup_dir/$backup_date
cp -r $namenode_dir $journalnode_dir $backup_dir/$backup_date
echo `date` "backup namenode data dir success..."
