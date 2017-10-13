#!/usr/bin/env bash

base_dir=$(dirname $0)
prefix_name=$1
log_dir=$2
nfs_dir=/data/backups/logcenter/temp_20170831

raw_list=${base_dir}/raw_list.log
log_file=${base_dir}/rename.log

ls ${log_dir} > ${raw_list}

prefix_name_length=${#prefix_name}
echo "prefix_name_length is ${prefix_name_length}"
cat ${raw_list} |while read line
do
  echo "raw filename ${log_dir}/$line ,and rename to ${nfs_dir}/${line:${prefix_name_length}}"
  cp ${log_dir}/$line ${nfs_dir}/${line:${prefix_name_length}}
done



#   sh rename.sh _data_logs_logcenter_current--- /home/moretv/test