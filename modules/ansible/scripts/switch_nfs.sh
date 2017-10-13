#!/usr/bin/env bash
# sh  swich.sh 10.255.130.6
HOSTIP=$1

MOUNT_NOW=`df -h|grep /data/backups |awk -F":" '{print $1}'`
if [ $MOUNT_NOW == $HOSTIP ];then
    echo "Use correct Device "
else
    umount /data/backups
    mount  -t nfs  $HOSTIP:/data/backups /data/backups
fi
