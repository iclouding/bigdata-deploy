# -*- coding: utf-8 -*-
# !/usr/bin/env python

from ftplib import FTP
import os
import time


def ftp_up(filename):
    ftp = FTP()
    ftp.set_debuglevel(2)  # 打开调试级别2，显示详细信息;0为关闭调试信息
    ftp.connect('10.10.150.244', '21')  # 连接
    ftp.login('ftpuser', 'gZy4humhqb5wosUc')  # 登录，如果匿名登录则用空串代替即可
    # print ftp.getwelcome()#显示ftp服务器欢迎信息
    # ftp.cwd('xxx/xxx/') #选择操作目录
    bufsize = 1024  # 设置缓冲块大小
    file_handler = open(filename, 'rb')  # 以读模式在本地打开文件
    ftp.storbinary('STOR %s' % os.path.basename(filename), file_handler, bufsize)  # 上传文件
    ftp.set_debuglevel(0)
    file_handler.close()
    ftp.quit()
    print "ftp up OK"


def str_day():
    base_time = time.time()
    return time.strftime("%Y-%m-%d", time.localtime(base_time))


def str_filename():
    days = str_day()
    filename = r"d:\backup\tabserver_backup-%s.tsbak" % days
    return filename


if __name__ == "__main__":
    filename = str_filename()
    ftp_up(filename)
