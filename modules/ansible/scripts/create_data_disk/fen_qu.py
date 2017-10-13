#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
date: 2017/02/09
role: 大数据分区临时脚本
usage: fen_qu.py
'''
import os
import sys

from yunwei.operate.prefix import log, exclusiveLock, execShell

reload(sys)
sys.setdefaultencoding("utf-8")


###分区
def fen_qu():
    ###字典
    cipan_num = {'sda': '/data1', 'sdb': '/data2', 'sdc': '/data3', 'sdd': '/data4', 'sde': '/data5', 'sdf': '/data6', 'sdg': '/data7', 'sdh': '/data8', 'sdi': '/data9', 'sdj': '/data10', 'sdk': '/data11', 'sdl': '/data12', 'sdm': '/data13', 'sdn': '/data14', 'sdp': '/data'}

    ###循环
    for k, v in cipan_num.items():
        base_dir = '/dev'
        dev_path = os.path.join(base_dir, k)

        #1
        mklab_cmd = 'parted %s mklabel gpt' % dev_path
        print k, mklab_cmd
        get_status_mklab, get_output_mklab = execShell(mklab_cmd)
        if get_status_mklab != 0:
            logIns.writeLog('debug', '%s' % get_output_mklab)

        #2
        mkpar_cmd = 'parted %s mkpart primary xfs 2048s 100%%' % dev_path
        print k, mkpar_cmd
        get_status_mkpar, get_output_mkpar = execShell(mkpar_cmd)
        if get_status_mkpar != 0:
            logIns.writeLog('debug', '%s' % get_output_mkpar)

        #3
        mkxfs_cmd = 'mkfs.xfs -f %s' % dev_path
        print k, mkxfs_cmd
        get_status_mkxfs, get_output_mkxfs = execShell(mkxfs_cmd)
        if get_status_mkxfs != 0:
            logIns.writeLog('debug', '%s' % get_output_mkxfs)

        #4
        mount_cmd = 'mkdir %s && mount %s %s' % (v, dev_path, v)
        print k, mount_cmd
        get_status_mount, get_output_mount = execShell(mount_cmd)
        if get_status_mount != 0:
            logIns.writeLog('debug', '%s' % get_output_mount)

        #5
        blkid_cmd = 'blkid %s' % dev_path
        print k, blkid_cmd
        get_status_blkid, get_output_blkid = execShell(blkid_cmd)
        if get_status_blkid != 0:
            logIns.writeLog('debug', '%s' % get_output_blkid)

        #6
        uuid = get_output_blkid.split('=')[1].split('\"')[1]
        print k, uuid
        txt_values = 'UUID=%s %s xfs defaults 0 0' % (uuid, v)
        fstab_cmd = 'echo "%s" >> /etc/fstab' % txt_values
        get_status_fstab, get_output_fstab = execShell(fstab_cmd)
        if get_status_fstab != 0:
            logIns.writeLog('debug', '%s' % get_output_fstab)


if __name__ == "__main__":
    ###脚本名
    script_name = os.path.basename(__file__)
    sub_name = script_name.split('.')[0]

    ###日志路径
    log_path = '/log/yunwei/%s.log' % script_name

    ###定义日志标识
    logIns = log('1074', log_path, display=True)
    logMain = log('01074', '/log/yunwei/yunwei.log', display=True)

    print "start"

    ###分区
    fen_qu() 

    print "end"
