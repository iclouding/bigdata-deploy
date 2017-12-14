# -*- coding: utf-8 -*-
"""[summary]
VR bi数据同步脚本，通过azkaban每日进行调度，将昨天的数据从hdfs打包上传到VR指定的服务器
[description]
"""

import os
import re
import shutil
from ftplib import FTP, error_perm
import time
import sys

config = {'ftp_user': 'metisftp', 'ftp_pswd': 'gZy4humhqb5wosUc', 'ftp_host': '10.19.168.100',
    'localpath': '/tmp/hdfs2ftp', 'hdfspath': '/data_warehouse/ods_origin.db/log_raw/', 'ftppath': 'BIData'}


def logMsg(fun_name, err_msg, level):
    import logging, sys
    message = fun_name + ':' + err_msg
    logger = None
    logger = logging.getLogger()
    logname = sys.argv[0] + '.log'
    hdlr = logging.FileHandler(logname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)  # 网络上的实现基本为说明这条语句的使用和作用


def run_cmd(cmd):
    import subprocess
    msg = "Starting run: %s " % cmd
    logMsg("run_cmd", msg, 1)
    cmdref = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error_info = cmdref.communicate()
    if error_info:
        if isinstance(error_info, list) or isinstance(error_info, tuple):
            error_info = error_info[0]
        msg = "RUN %s ERROR,error info:  %s" % (cmd, error_info)
        logMsg("run_cmd", msg, 2)
        return 0, error_info
    else:
        msg = "run %s success" % cmd
        logMsg("cmd", msg, 1)
        # print "Run Success!!"
        return 1, output


class ftpBase():
    def __init__(self, **args):
        ###获取参数
        self.host = args.get('ftp_host')
        self.user = args.get('ftp_user')
        self.pswd = args.get('ftp_pswd')
        self.port = args.get('ftp_port', 21)
        self.timeout = args.get('time_out', 60)

        ###连接
        try:
            self.ftp = FTP()
            self.ftp.connect(self.host, self.port, self.timeout)
            self.ftp.login(self.user, self.pswd)
        except:
            logMsg('init', '%s connect error' % self.host, 2)
            raise ValueError(' connect error %s' % self.host)

    ###析构函数
    def __del__(self):
        self.ftp.close()

    def _checkDir(self, check_dir):
        ###确认远程目录是否存在
        dirs = check_dir.split('/')
        for sub_dir in dirs:
            if sub_dir:
                try:
                    self.ftp.cwd(sub_dir)
                except error_perm:
                    try:
                        self.ftp.mkd(sub_dir)
                        self.ftp.cwd(sub_dir)
                    except error_perm:
                        logMsg("check_dir", 'U have no authority to make dir %s' % sub_dir, 2)

    ###上传文件
    def uploadFile(self, local_path, remote_path):
        ###判断本地文件
        if not os.path.isfile(local_path):
            logMsg('upload', '%s not exists' % local_path, 2)
            raise ValueError('%s not exists' % local_path)

        self._checkDir(remote_path)
        # ###上传的目录
        # remote_dir = self.ftp.pwd()
        up_cmd = "ncftpput -z -u%s -p%s %s %s %s" % (self.user, self.pswd, self.host, remote_path, local_path)
        logMsg("cmd", up_cmd, 1)
        (get_status_up, get_output_up) = run_cmd(up_cmd)
        ###确认是否执行成功2
        if (get_status_up == 0):
            logMsg('uoload', '%s upload error' % local_path, 2)
            raise ValueError('%s upload error' % local_path)

    ###上传目录
    def uploadDir(self, local_dir='./', remote_dir='./'):
        if not os.path.isdir(local_dir):
            logMsg('updir', '%s not exists' % self.local_dir, 2)
            raise ValueError('%s not exists' % self.local_dir)

        ###创建目录
        all_dirs = remote_dir.split(',')
        for all_dir in all_dirs:
            try:
                self.ftp.mkd(all_dir)
            except:
                pass
            self._checkDir(all_dir)

        ###进入目录
        self._checkDir(remote_dir)

        ###遍历本地目录
        for file in os.listdir(local_dir):
            src = os.path.join(local_dir, file)
            if os.path.isfile(src):
                self.uploadFile(src, file)
            elif os.path.isdir(src):
                try:
                    self.ftp.mkd(file)
                except:
                    pass
                self.uploadDir(src, file)
        self.ftp.cwd('..')

    ###打印列表
    def listDir(self, remote_dir='./'):
        self._checkDir(remote_dir)
        return self.ftp.dir()

    ###查找远程目录或文件
    def findFile(self, file_name, remote_dir='./'):
        self._checkDir(remote_dir)
        all_files = self.ftp.nlst()

        ###匹配则输出
        retu_files = []
        for all_file in all_files:
            if re.search(r'%s' % file_name, all_file):
                retu_files.append(all_file)

        ###返回
        return retu_files

    ###下载文件
    def downloadFile(self, local_path, remote_path):
        ###备份旧文件
        if os.path.isfile(local_path):
            shutil.move(local_path, "%s.%s" % (local_path, "old"))

        ###下载文件
        try:
            fp_ftp = open(local_path, 'wb').write
            self.ftp.retrbinary('RETR %s' % remote_path, fp_ftp)
        except:
            down_cmd = "wget ftp://%s:%s@%s/%s -P %s" % (
                self.user, self.pswd, self.host, remote_path, os.path.dirname(local_path))
            (get_status_down, get_output_down) = run_cmd(down_cmd)
            ###确认是否执行成功
            if (get_status_down == 0):
                logMsg('down', '%s download error' % remote_path, 2)
                raise ValueError('%s download error' % remote_path)

    ###下载目录
    def downloadDir(self, local_dir='./', remote_dir='./'):
        ###创建本地目录
        if not os.path.isdir(local_dir):
            os.makedirs(local_dir)

        ###进入目录
        self._checkDir(remote_dir)

        ###获取远程所有文件
        remote_files = self.listDir(remote_dir)
        for item in remote_files:
            file_type = item[0]
            file_name = item[1]
            local_base = os.path.join(local_dir, file_name)
            if file_type == 'd':
                self.downloadDir(local_base, file_name)
            elif file_type == '-':
                self.downloadFile(local_base, file_name)

        self.ftp.cwd('..')


def checkLocalPath(localpath, suffix):
    checkPath = "%s/%s" % (localpath, suffix)
    if not os.path.isdir(checkPath):
        mkdir_localpath_cmd = "mkdir -p %s" % checkPath
        run_cmd(mkdir_localpath_cmd)
        logMsg("checkpath", "no found path in local %s ,make it!" % checkPath, 2)
    if os.path.isdir(checkPath):
        cmd = "cd  %s;rm -f *" % checkPath
        run_cmd(cmd)
        logMsg("checkpath", "find path in local %s ,remove it!" % checkPath, 2)


def getFromHdfs(suffix):
    localpath = config['localpath']
    hdfspath = config['hdfspath']
    checkLocalPath(localpath, suffix)
    current_local = "%s/%s" % (localpath, suffix)
    # su - hdfs -c 'hadoop fs -get /log/vr/rawlog/20170612  /tmp'
    cmd = 'hadoop fs -get  %s/key_day=%s/key_hour=*/boikgpokn78sb95kbqei6cc98dc5mlsr.log*   %s ' % (
    hdfspath, suffix, current_local)
    k, v = run_cmd(cmd)
    if k == 1:
        return True
    else:
        msg = "run cmd %s Failed !" % cmd
        logMsg("update2hdfs", msg, 2)
        raise RuntimeError("get From Hdfs Failed")


def putToFtp(suffix):
    localpath = config['localpath']
    filename = os.path.join(localpath, "%s.tar.gz" % suffix)
    ftp_args = dict()
    ftp_args['ftp_host'] = config['ftp_host']
    ftp_args['ftp_user'] = config['ftp_user']
    ftp_args['ftp_pswd'] = config['ftp_pswd']
    ftp_args['ftp_port'] = 21
    ftp_args['timeout'] = 60
    ftppath = config['ftppath']
    fb = ftpBase(**ftp_args)
    # path = "/".join(filename.split('/')[:-1])
    fb.uploadFile(filename, remote_path=ftppath)
    logMsg("FTP", 'Upload %s to ftp success' % filename, 1)
    return True


def makeTarFiles(suffix):
    localpath = config['localpath']
    cmd = "cd %s&& tar zcvf %s.tar.gz %s" % (localpath, suffix, suffix)
    k, v = run_cmd(cmd)
    if k == 1:
        return True
    else:
        msg = "run cmd %s Failed !" % cmd
        logMsg("makeTarFiles", msg, 2)
        raise RuntimeError("make Tar Files Failed")


def main():
    if len(sys.argv) == 1:
        yesterday = time.time() - 24 * 3600
        suffix = time.strftime("%Y%m%d", time.localtime(yesterday))
    else:
        suffix = sys.argv[1]
    if getFromHdfs(suffix):
        if makeTarFiles(suffix):
            putToFtp(suffix)


if __name__ == "__main__":
    main()
