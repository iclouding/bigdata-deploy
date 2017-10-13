#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
读取文本中列表信息，判断FTP是否存在文件，如果存在打错误日志，否则依次上传
'''
import os
import sys
from common import logMsg, run_cmd, read_files
from  ftplib import FTP
import pdb

ftp_ip1 = "106.75.91.71"
ftp_ip2 = "106.75.91.77"
ftp_ip = ftp_ip1
ftp_user = "logback"
ftp_passwd = "qosa18WEbkq"


def ftp_up(files):
    pdb.set_trace()
    if not ftp_check(files):
        ftp_cmd = "put %s bigdata_hdfs" % files
        cmd = "lftp -u %s,%s -e'%s;bye' %s" % (ftp_user, ftp_passwd, ftp_cmd, ftp_ip)
        msg = "put file %s" % files
        logMsg("up", msg, 1)
        run_cmd(cmd)
    else:
        msg_err = "files %s was in ftp " % files
        logMsg("check", msg_err, 2)


def ftp_check(files):
    pdb.set_trace()
    ftp = FTP(ftp_ip)
    ftp.login(ftp_user, ftp_passwd)
    check_file = "bigdata_hdfs/" + files.split(r'/')[-1]
    try:
        size = ftp.size(check_file)
        return True
    except:
        msg_err = "files %s was in ftp " % files
        logMsg("check", msg_err, 2)
        return False


def main():
    filename = sys.argv[1]
    data = read_files(filename).split('\n')
    for line in data:
        ftp_up(line)


if __name__ == "__main__":
    main()
