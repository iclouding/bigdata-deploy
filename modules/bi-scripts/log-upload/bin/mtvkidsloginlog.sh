#!/bin/bash
DAY=$1
HOST_1=10.10.225.237
HOST_2=10.10.229.4
HOST_3=10.10.248.218
HOST_4=10.10.248.84

function download_log(){
  HOST=$1
  DAY=$2
  USER=moretv
  PASS='MoreTV_!@#&666&!'
  echo "Starting to sftp…"
  lftp -u ${USER},${PASS} sftp://${HOST} <<EOF
    cd /data/log/kids_log/
    lcd /data/backups/mtvkids_loginlog/
    mget mtvkidsloginlog.access.log_${DAY}-kidslogin-portalu-*.bz2
    bye
EOF
  echo "done"
}

download_log $HOST_1 $DAY
download_log $HOST_2 $DAY
download_log $HOST_3 $DAY
download_log $HOST_4 $DAY
