# -*- coding: utf-8 -*-
"""
logcenter上传HDFS

"""
import commands
import json
import logging
import os
import re
from collections import defaultdict
import socket
import arrow
import requests
import log_lograte_config
import sys


def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = logging.getLogger()
    base_name = log_lograte_config.logs
    base_time = arrow.utcnow().to("Asia/Shanghai").format("YYYYMMDD")
    logname = "%s/%s_%s" % ('/'.join(base_name.split('/')[0:-1]), base_time, base_name.split('/')[-1])
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
    mysub = "log_lograte %s " % socket.gethostname()
    mail_content["sub"] = mysub + sub
    mail_content["content"] = body
    mail_content["sendto"] = log_lograte_config.sendto
    mail_url = 'http://10.19.15.127:5006/mail/api/v1.0/send'
    
    heads = {'content-type': 'application/json'}
    r = requests.post(url = mail_url, headers = heads, data = json.dumps(mail_content))
    if r.status_code == 200:
        log_msg("send_alter_mail", "send mail success", 1)
    else:
        err_msg = "send mail failed ,output was %s" % r.content
        log_msg("send_alter_mail", err_msg, 2)


def run_cmd(cmd):
    (status, output) = commands.getstatusoutput(cmd)
    if status == 0:
        log_msg("run_cmd", "run %s success!" % cmd, 1)
        return True
    else:
        msg = "run %s Failed,output was %s " % (cmd, output)
        log_msg("run_cmd", msg, 2)
        return False


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


def _list_local_files(path):
    all_local_files = list()
    all_local = os.listdir(path)
    for item in all_local:
        if os.path.isfile(os.path.join(path, item)):
            all_local_files.append(item)
    return all_local_files


def _check_filename_by_match_date(filename, up_file_date):
    pattern = "log\.(\w+)\.(\d{4}-\d{2}-\d{2}-\d{2})_bigdata-extsvr"
    match_values = re.match(pattern, filename)
    if match_values:
        file_time = match_values.group(2)
        if file_time in up_file_date:
            return True
    else:
        return False


def _check_files_by_hdfs(local_path):
    files_need_upload = list()
    hdfs_paths = list(set(local_path.values()))
    myhdfs = MyHdfs(hdfs_paths)
    hdfs_info = myhdfs.get_hdfs_info()
    for item in local_path.keys():
        if item not in hdfs_info.keys():
            files_need_upload.append(item)
    return files_need_upload


def _get_filedate(hour, step):
    file_data = list()
    for i in range(step):
        item = arrow.utcnow().to('Asia/Shanghai').shift(hours = -(int(hour) + i)).format("YYYYMMDDHH")
        file_data.append(item)
    return file_data


def _replace_hdfs_rule(values):
    hdfs_change = log_lograte_config.hdfs_change
    for item in hdfs_change.keys():
        if values == item:
            values = hdfs_change[item]
    return values


def _get_local_files_hdfs_path(filename):
    project = filename.split('.')[1]
    file_time = filename.split('.')[2]
    hdfs_time = file_time.split('_')[0].replace('-', '')[0:8]
    new_projec = _replace_hdfs_rule(project)
    hdfs_path = "/log/%s/rawlog/%s" % (new_projec, hdfs_time)
    return hdfs_path


def _up_local_2_hdfs(local_path, local_hdfs_path):
    poly_hdfs_info = defaultdict(list)
    run_status = True
    for items in local_hdfs_path.items():
        poly_hdfs_info[items[1]].append(items[0])
    
    for hdfs_path in poly_hdfs_info.keys():
        mkdir_hdfs_dir = "su - spark -c'/opt/hadoop/bin/hadoop fs -mkdir -p %s'" % hdfs_path
        if not run_cmd(mkdir_hdfs_dir):
            run_status = False
        
        upload_files = " ".join(poly_hdfs_info[hdfs_path])
        print "开始上传文件:%s" % upload_files
        up2_hdfs_cmd = "su - spark -c'cd %s && /opt/hadoop/bin/hadoop fs -put %s %s'" % (
            local_path, upload_files, hdfs_path)
        if not run_cmd(up2_hdfs_cmd):
            run_status = False
    return run_status


def _check_after_up(local_size, local_hdfs):
    no_found = list()
    diff_size = list()
    check_status = True
    
    myhdfs = MyHdfs(list(set(local_hdfs.values())))
    hdfs_info = myhdfs.get_hdfs_info()
    for item in local_size.keys():
        if item not in hdfs_info.keys():
            no_found.append(item)
        if int(local_size[item]) != int(hdfs_info[item]):
            diff_size.append(item)
    
    if no_found:
        msg_no_found = "下列文件未能上传到HDFS: %s" % ("\n".join(no_found))
        mail_sub_nofound = "文件未能上传成功"
        log_msg("_check_after_up", msg_no_found, 2)
        send_alter_mail(sub = mail_sub_nofound, body = msg_no_found)
        check_status = False
    
    if diff_size:
        mail_sub_diff = "本地文件与HDFS大小不一致"
        msg_diff = "本地文件与HDFS大小不一致:\n"
        for diff_file in diff_size:
            msg_diff += "filename %s ,Local %s ,hdfs %s \n" % (
                diff_size, str(local_size[diff_file], str(hdfs_info[diff_file])))
        log_msg("_check_after_up", msg_diff, 2)
        send_alter_mail(sub = mail_sub_diff, body = msg_diff)
        check_status = False
    return check_status


def up2hdfs_workflow(file_date):
    # 取得所有本地文件
    # 匹配logcent规则，获得符合标准的文件列表,  根据hour和step匹配出需要上传的文件列表
    # 检查HDFS 是否存在同名文件
    # 上传文件
    local_path = log_lograte_config.local_paths
    all_files = _list_local_files(local_path)
    local_check_files_hdfs_path = dict()
    for check_file in all_files:
        if _check_filename_by_match_date(check_file, file_date):
            local_check_files_hdfs_path[check_file] = _get_local_files_hdfs_path(check_file)
    
    files_need_upload = _check_files_by_hdfs(local_check_files_hdfs_path)
    
    if files_need_upload():
        local_size_info = dict()
        local_hdfs_path = dict()
        for file_need_upload in files_need_upload:
            local_size_info[file_need_upload] = os.path.getsize(os.path.join(local_path, file_need_upload))
            local_hdfs_path[file_need_upload] = _get_local_files_hdfs_path(file_need_upload)
        
        # 根据列表生成2个doct，local_size_info，记录文件大小,local_hdfs_path记录文件与远程HDFS对应关系
        
        if _up_local_2_hdfs(local_path, local_hdfs_path):
            if _check_after_up(local_size_info, local_hdfs_path):
                return True
            else:
                return False
        else:
            return False
    else:
        msg_no_files = "未发现需要上传的文件"
        log_msg("up2hdfs_workflow", msg_no_files, 1)
        return True


def main():
    # 如果没有输入任何参数，即默认上传前一小时文件的操作
    # 如果输入参数 hour 即默认Step=1，进行数据补传 ，如果输入2个参数 即hour和step
    if len(sys.argv) == 2:
        hour = 1
        step = 1
    elif len(sys.argv) == 3:
        hour = sys.argv[1]
        step = 1
    elif len(sys.argv) == 4:
        hour = sys.argv[1]
        step = sys.argv[2]
    else:
        msg_errror = "输入参数不符合脚本定义"
        log_msg("main", msg_errror, 2)
        raise RuntimeError(msg_errror)
    file_date = _get_filedate(hour = hour, step = step)
    if up2hdfs_workflow(file_date):
        log_msg("main", "文件上传完毕", 1)
    else:
        log_msg("main", "文件上传存在异常，请检查日志&邮件", 2)
        msg_error = "文件上传存在异常,请检查日志"
        mail_sub_error = "文件上传存在异常"
        send_alter_mail(sub = mail_sub_error, body = msg_error)


if __name__ == "__main__":
    try:
        main()
    except :
        import StringIO, traceback
        
        fp = StringIO.StringIO()
        traceback.print_exc(file = fp)
        message = fp.getvalue()
        msg_errror = "脚本运行异常 %s" % message
        mail_sub = "脚本运行异常"
        send_alter_mail(sub = mail_sub, body = msg_errror)
