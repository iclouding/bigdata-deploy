#!/bin/bash
DAY=$1
HOST_1=10.10.225.237
HOST_2=10.10.229.4
HOST_3=10.10.248.218
HOST_4=10.10.248.84
HOST_5=10.10.216.105
HOST_6=10.10.214.213

FtpDir_1="/data/log/openlogin_log/"
FtpDir_2="/data/log/login_log/"
FtpDir_3="/data/logs/medusa_login/"

Password_1="MoreTV_!@#&666&!"
Password_2="moretv2015!@#"

function download_log(){
  HOST=$1
  DAY=$2
  FtpDir=$3
  USER=moretv
  PASS=$4
  echo "Starting to sftp…"
  lftp -u ${USER},${PASS} sftp://${HOST} <<EOF
    cd $FtpDir
    lcd /data/backups/moretv_loginlog/
    mget loginlog.access.log_${DAY}*.bz2
    bye
EOF
  echo "done"
}

download_log $HOST_1 $DAY $FtpDir_1 $Password_1
download_log $HOST_2 $DAY $FtpDir_1 $Password_1
download_log $HOST_3 $DAY $FtpDir_1 $Password_1
download_log $HOST_4 $DAY $FtpDir_1 $Password_1

download_log $HOST_1 $DAY $FtpDir_2 $Password_1
download_log $HOST_2 $DAY $FtpDir_2 $Password_1
download_log $HOST_3 $DAY $FtpDir_2 $Password_1
download_log $HOST_4 $DAY $FtpDir_2 $Password_1

download_log $HOST_5 $DAY $FtpDir_3 $Password_2
download_log $HOST_6 $DAY $FtpDir_3 $Password_2
