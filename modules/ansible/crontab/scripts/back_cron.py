# -*- coding: utf-8 -*-
'''
按日期打包本机所有用户的crontab文件，并上传到FTP服务器

'''
import commands
import os
import re
import shutil
from ftplib import FTP, error_perm
import arrow

DEBUG = False
config = {'ftp_user': 'miles', 'ftp_pswd': 'aspect', 'ftp_host': '10.255.130.6', 'ftppath': 'back_cron'}


def log_msg(fun_name, err_msg, level):
    import logging, sys
    message = fun_name + ':' + err_msg
    # logger = None
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
    if DEBUG:
        status = 0
        output = ""
    else:
        (status, output) = commands.getstatusoutput(cmd)
    if status == 0:
        log_msg("run_cmd", "run %s sucess!" % cmd, 1)
        return True
    else:
        error_msg = "run %s Failed,output was %s" % (cmd, output.strip())
        log_msg("run_cmd", error_msg, 2)
        raise RuntimeError


class ftpBase():
    def __init__(self, **args):
        # 获取参数
        self.host = args.get('ftp_host')
        self.user = args.get('ftp_user')
        self.pswd = args.get('ftp_pswd')
        self.port = args.get('ftp_port', 21)
        self.timeout = args.get('time_out', 60)
        
        # 连接
        try:
            self.ftp = FTP()
            self.ftp.connect(self.host, self.port, self.timeout)
            self.ftp.login(self.user, self.pswd)
        except:
            log_msg('init', '%s connect error' % self.host, 2)
            raise ValueError(' connect error %s' % self.host)
    
    # 析构函数
    def __del__(self):
        self.ftp.close()
    
    def _checkDir(self, check_dir):
        # 确认远程目录是否存在
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
                        log_msg("check_dir", 'U have no authority to make dir %s' % sub_dir, 2)
    
    # 上传文件
    def uploadFile(self, local_file, remote_path):
        # 判断本地文件
        if not os.path.isfile(local_file):
            log_msg('upload', '%s not exists' % local_file, 2)
            raise ValueError('%s not exists' % local_file)
        
        self._checkDir(remote_path)
        # # 上传的目录
        # remote_dir = self.ftp.pwd()
        up_cmd = "ncftpput -z -u%s -p%s %s %s %s" % (self.user, self.pswd, self.host, remote_path, local_file)
        log_msg("cmd", up_cmd, 1)
        #(get_status_up, get_output_up) = run_cmd(up_cmd)
        # 确认是否执行成功2
        if not run_cmd(up_cmd):
            log_msg('uoload', '%s upload error' % local_file, 2)
            raise ValueError('%s upload error' % local_file)
    
    # 上传目录
    def uploadDir(self, local_dir = './', remote_dir = './'):
        if not os.path.isdir(local_dir):
            log_msg('updir', '%s not exists' % self.local_dir, 2)
            raise ValueError('%s not exists' % self.local_dir)
        
        # 创建目录
        all_dirs = remote_dir.split(',')
        for all_dir in all_dirs:
            try:
                self.ftp.mkd(all_dir)
            except:
                pass
            self._checkDir(all_dir)
        
        # 进入目录
        self._checkDir(remote_dir)
        
        # 遍历本地目录
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
    
    # 打印列表
    def listDir(self, remote_dir = './'):
        self._checkDir(remote_dir)
        return self.ftp.dir()
    
    # 查找远程目录或文件
    def findFile(self, file_name, remote_dir = './'):
        self._checkDir(remote_dir)
        all_files = self.ftp.nlst()
        
        # 匹配则输出
        retu_files = []
        for all_file in all_files:
            if re.search(r'%s' % file_name, all_file):
                retu_files.append(all_file)
        
        # 返回
        return retu_files
    
    # 下载文件
    def downloadFile(self, local_path, remote_path):
        # 备份旧文件
        if os.path.isfile(local_path):
            shutil.move(local_path, "%s.%s" % (local_path, "old"))
        
        # 下载文件
        try:
            fp_ftp = open(local_path, 'wb').write
            self.ftp.retrbinary('RETR %s' % remote_path, fp_ftp)
        except:
            down_cmd = "wget ftp://%s:%s@%s/%s -P %s" % (
                self.user, self.pswd, self.host, remote_path, os.path.dirname(local_path))
            # (get_status_down, get_output_down) = run_cmd(down_cmd)
            # 确认是否执行成功
            if not run_cmd(down_cmd):
                log_msg('down', '%s download error' % remote_path, 2)
                raise ValueError('%s download error' % remote_path)
    
    # 下载目录
    def downloadDir(self, local_dir = './', remote_dir = './'):
        # 创建本地目录
        if not os.path.isdir(local_dir):
            os.makedirs(local_dir)
        
        # 进入目录
        self._checkDir(remote_dir)
        
        # 获取远程所有文件
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


class backCrontab():
    def __init__(self):
        self.base_dir = "/data/backups/crontab"
        self.hostname = self._get_hostname()
        self.now = self._get_date()
        self.back_filename = "{hostname}_{now}_cronbak.tar.gz".format(hostname = self.hostname, now = self.now)
    
    def _get_hostname(self):
        import socket
        hostname = socket.gethostname()
        return hostname
    
    def _get_date(self):
        utc = arrow.now('Asia/Shanghai').format("YYYYMMDDHH")
        return utc
    
    def back_crontab(self):
        # 检查base_dir是否存在，不在则创建
        if not os.path.isdir(self.base_dir):
            commands.getoutput("mkdir -p %s" % self.base_dir)
        # 生成Tar文件
        full_file = "{base_dir}/{filename}".format(base_dir = self.base_dir, filename = self.back_filename)
        bak_cmd = "tar zcvf {full_file} /var/spool/cron".format(full_file = full_file)
        run_cmd(bak_cmd)
        
        # 上传到FTP
        self._up_ftp(full_file)
        return True
    
    def _up_ftp(self, filename):
        ftp_args = dict()
        ftp_args['ftp_host'] = config['ftp_host']
        ftp_args['ftp_user'] = config['ftp_user']
        ftp_args['ftp_pswd'] = config['ftp_pswd']
        ftp_args['ftp_port'] = 21
        ftp_args['timeout'] = 60
        ftppath = config['ftppath']
        remopath="%s/%s"%(ftppath,arrow.now('Asia/Shanghai').format("YYYYMMDD"))
        fb = ftpBase(**ftp_args)
        # path = "/".join(filename.split('/')[:-1])
        fb.uploadFile(filename, remote_path = remopath)
        log_msg("FTP", 'Upload %s to ftp success' % filename, 1)
        return True


if __name__ == "__main__":
    mycrontab = backCrontab().back_crontab()
