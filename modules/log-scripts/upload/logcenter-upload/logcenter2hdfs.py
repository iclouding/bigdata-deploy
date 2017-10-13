# -*- coding: utf-8 -*-
import commands
import json
import logging
import os
import re
from collections import defaultdict
import arrow
import requests
import logcenter2hdfs_config
import pdb
import socket


def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = logging.getLogger()
    logname = logcenter2hdfs_config.logs
    hdlr = logging.FileHandler(logname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)


def send_alter_mail(sub, body):
    mail_content = dict()
    mysub = "Logcenter upload %s " % socket.gethostname()
    mail_content["sub"] = mysub + sub
    mail_content["content"] = body
    mail_content["sendto"] = logcenter2hdfs_config.sendto
    mail_url = 'http://10.19.15.127:5006/mail/api/v1.0/send'
    
    heads = {'content-type': 'application/json'}
    r = requests.post(url = mail_url, headers = heads, data = json.dumps(mail_content))
    if r.status_code == 200:
        log_msg("send_alter_mail", "send mail success", 1)
    else:
        err_msg = "send mail failed ,output was %s" % r.content
        log_msg("send_alter_mail", err_msg, 2)


def run_cmd(cmd):
    dry_run = logcenter2hdfs_config.debug
    if dry_run:
        status = 0
    else:
        (status, output) = commands.getstatusoutput(cmd)
    # status=0
    if status == 0:
        log_msg("run_cmd", "run %s success!" % cmd, 1)
        return True
    else:
        msg = "run %s Failed,output was %s " % (cmd, output)
        log_msg("run_cmd", msg, 2)
        return False


class MyLocal():
    """
     处理本地文件规则

     """
    
    def __init__(self, path):
        self.path = path
        self.hdfs_change = logcenter2hdfs_config.hdfs_change
        self.hours = logcenter2hdfs_config.hours
        self.before = arrow.utcnow().shift(hours = -int(logcenter2hdfs_config.hours)).timestamp
    
    def _list_local_files(self):
        all_local_files = list()
        all_local = os.listdir(self.path)
        for item in all_local:
            if os.path.isfile(os.path.join(self.path, item)):
                all_local_files.append(item)
        return all_local_files
    
    def _split_filename_hdfs(self, filename):
        pattern = "log\.(\w+)\.(\d{4}-\d{2}-\d{2}-\d{2})_bigdata-extsvr"
        # filename like  log.helios.2017-09-06-09_bigdata-extsvr-log2_2.log
        match_values = re.match(pattern, filename)
        if match_values:
            file_time = match_values.group(2)
            return file_time
        else:
            return None
    
    def return_match_files(self):
        all_files = self._list_local_files()
        local_files_info = dict()
        local_hdfspath = dict()
        for item in all_files:
            datetime = self._split_filename_hdfs(item)
            if datetime:
                file_datetime = "{year}-{month}-{day} {hour}:00:00".format(year = datetime[0:4], month = datetime[5:7],
                                                                           day = datetime[8:10], hour = datetime[11:13])
                file_timestamp = arrow.get(file_datetime).timestamp
                if int(file_timestamp) > int(self.before):
                    local_files_info[item] = os.path.getsize(os.path.join(self.path, item))
                    local_hdfspath[item] = self._str_hdfs_path(item)
        return local_files_info, local_hdfspath
    
    def _str_hdfs_path(self, filename):
        """
        按本地文件名计算出HDFS对应的上传路径
        :param filename: 本地文件名
        :return: HDFS上传路径
        """
        project = filename.split('.')[1]
        file_time = filename.split('.')[2]
        hdfs_time = file_time.split('_')[0].replace('-', '')[0:8]
        new_projec = self._replace_hdfs_rule(project)
        hdfs_path = "/log/%s/rawlog/%s" % (new_projec, hdfs_time)
        return hdfs_path
    
    def _replace_hdfs_rule(self, values):
        for item in self.hdfs_change.keys():
            if values == item:
                values = self.hdfs_change[item]
        return values


class MyHdfs():
    """
    获得HDFS路径下所有文件信息
    输入HDFS路径,可多个路径按“，”分割
    因HDFS路径由本地文件名转换而来，不存在相同文件名存在不同路径下的可能
    返回这些路径下所有文件大小
    """
    
    def __init__(self, path):
        self.path = path
    
    def get_hdfs_info(self):
        hdfs_info = dict()
        for hdfs_one in self.path:
            cmd = "su - spark -c '/opt/hadoop/bin/hadoop fs -ls %s'" % hdfs_one
            status, output = commands.getstatusoutput(cmd)
            if status == 0 and len(output.split('\n')) > 1:
                for line in output.split('\n'):
                    if line[0] == '-':
                        hdfs_info[line.split()[7].split('/')[-1]] = line.split()[4]
            else:
                msg = "get %s from hadoop failed ,output was %s" % (self.path, output)
                log_msg("_get_hdfs_file_list", msg, 2)
        
        return hdfs_info


class HdfsCommands():
    def __init__(self, local_path):
        self.retry = logcenter2hdfs_config.retry
        self.local_path = local_path
        # 获得本地需上传文件列表
        self.local_info, self.local_hdfs = MyLocal(self.local_path).return_match_files()
        # 获得HDFS路径下所有文件信息
        self.hdfs_paths = list(set(self.local_hdfs.values()))
        self.hdfs_info = MyHdfs(self.hdfs_paths).get_hdfs_info()
    
    def up2hdfs(self):
        """
        上传本地文件到HDFS，且进行检查，如失败重传1次
        输入:local_info dict,本地文件及大小
        输入：local_hdfs dict:本地文件及上传路径
        :return: True OR False
        """
        i = 1
        while i < self.retry:
            self._get_upload_list_hdfs()
            if self.local_info:
                if self._up_commnads():
                    if self._check_after_up():
                        return True
                    else:
                        msg_error = "本地路径%s上传失败，重传" % self.local_path
                        log_msg("up2hdfs", msg_error, 2)
                
                else:
                    i += 1
                    print "重传%s" % self.local_path
            else:
                msg_success = "没有发现需要上传的文件"
                log_msg("up2hdfs", msg_success, 1)
                return True
        
        msg_error = "上传%s连续失败，请人工介入" % self.local_path
        mail_sub = "连续上传失败"
        send_alter_mail(sub = mail_sub, body = msg_error)
        log_msg("up2hdfs", msg_error, 2)
        return False
    
    def _check_after_up(self):
        new_hdfs_info = MyHdfs(self.hdfs_paths).get_hdfs_info()
        for item in self.local_info.keys():
            if item not in new_hdfs_info.keys():
                return False
            if int(self.local_info[item]) != int(new_hdfs_info[item]):
                return False
        return True
    
    def _up_commnads(self):
        # 按HDFS路径做聚合上传
        poly_hdfs_info = defaultdict(list)
        run_status = True
        
        for items in self.local_hdfs.items():
            poly_hdfs_info[items[1]].append(items[0])
        
        for hdfs_path in poly_hdfs_info.keys():
            mkdir_hdfs_dir = "su - spark -c'/opt/hadoop/bin/hadoop fs -mkdir -p %s'" % hdfs_path
            if not run_cmd(mkdir_hdfs_dir):
                run_status = False
            
            upload_files = " ".join(poly_hdfs_info[hdfs_path])
            print "开始上传文件:%s" % upload_files
            up2_hdfs_cmd = "su - spark -c'cd %s && /opt/hadoop/bin/hadoop fs -put %s %s'" % (
            self.local_path, upload_files, hdfs_path)
            if not run_cmd(up2_hdfs_cmd):
                run_status = False
        return run_status
    
    def _get_upload_list_hdfs(self):
        # remove与HDFS大小一致的文件，检查是否有与 HDFS大小不一致的文件
        for item in self.local_info.keys():
            
            # 如果HDFS文件存在，且与本地大小一致
            if item in self.hdfs_info.keys():
                if int(self.local_info[item]) == int(self.hdfs_info.get(item, 0)):
                    del self.local_info[item]
                    del self.local_hdfs[item]
                
                # 如果HDFS文件存在，且与本地大小不一致
                # if int(self.local_info[item]) != int(self.hdfs_info.get(item, 0)):
                else:
                    msg_err = "HDFS 文件大小不一致：Filename {filename} ，LocalSize {local_size} ,HdfsSize {hdfs_size}".format(
                            filename = item, local_size = self.local_info[item],
                            hdfs_size = self.hdfs_info.get(item, 0))
                    log_msg("_get_upload_list_hdfs", msg_err, 2)
                    mail_sub = "HDFS 本地与HDFS大小不一致,请人工介入"
                    send_alter_mail(sub = mail_sub, body = msg_err)
                    del self.local_info[item]
                    del self.local_hdfs[item]


def main():
    local_path = logcenter2hdfs_config.paths
    my_up = HdfsCommands(local_path)
    my_up.up2hdfs()


if __name__ == "__main__":
    try:
        main()
    except:
        import StringIO, traceback
        
        fp = StringIO.StringIO()
        traceback.print_exc(file = fp)
        message = fp.getvalue()
        # info = sys.exc_info()
        msg_errror = "脚本运行异常 %s" % message
        mail_sub = "脚本运行异常"
        send_alter_mail(sub = mail_sub, body = msg_errror)

