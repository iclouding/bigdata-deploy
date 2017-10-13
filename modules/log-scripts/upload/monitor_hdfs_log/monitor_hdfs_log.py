# -*- coding: utf-8 -*-
import commands
import arrow
import logging
import sys
import os
import requests
import monitor_hdfs_log_config
import json
import pdb
import re
import socket


def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = logging.getLogger()
    logname = monitor_hdfs_log_config.logs
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
    mysub = "Monitor_hdfs_log %s " % socket.gethostname()
    mail_content["sub"] = mysub + sub
    mail_content["content"] = body
    mail_content["sendto"] = monitor_hdfs_log_config.sendto
    mail_url = 'http://10.19.15.127:5006/mail/api/v1.0/send'
    
    heads = {'content-type': 'application/json'}
    r = requests.post(url = mail_url, headers = heads, data = json.dumps(mail_content))
    if r.status_code == 200:
        log_msg("send_alter_mail", "send mail success", 1)
    else:
        err_msg = "send mail failed ,output was %s" % r.content
        log_msg("send_alter_mail", err_msg, 2)


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
                        # hdfs_info[line.split()[7].split('/')[-1]] = line.split()[4]
                        hdfs_info[line.split()[7]] = line.split()[4]
            else:
                msg = "get %s from hadoop failed ,output was %s" % (self.path, output)
                log_msg("_get_hdfs_file_list", msg, 2)
        
        return hdfs_info


class MyLocal():
    def __init__(self):
        self.rule1_index = monitor_hdfs_log_config.rule1_index
        self.rule1_project = monitor_hdfs_log_config.rule1_project
        self.rule_hostname = monitor_hdfs_log_config.rule_hostname
        self.appids = monitor_hdfs_log_config.appids
        self.hours = monitor_hdfs_log_config.hours
        self.rule_date_str1 = monitor_hdfs_log_config.rule_date_str1.upper()
        self.rule_date_str2 = monitor_hdfs_log_config.rule_date_str2.upper()
        self.rule_date_str3 = monitor_hdfs_log_config.rule_date_str3.upper()
        self.rule_date_str4 = monitor_hdfs_log_config.rule_date_str4.upper()
        self.datetime_check = self._get_datetime_check()
    
    def _get_datetime_check(self):
        check_datetime = list()
        for i in range(self.hours):
            check_datetime.append(arrow.utcnow().to('Asia/Shanghai').shift(hours = -(i + 1)))
        return check_datetime
    
    def _str_filename_rule1(self):
        check_filename = dict()
        # 构造rule1文件名 ""/log/{rule1_project_keys}/rawlog/{rule_date_str1}/log.{rule1_project_values}.{rule_date_str2}_{hostname}_{rule1_index}.log""
        rule1_file_pattern = monitor_hdfs_log_config.rule1_file_pattern
        for rule1_project_keys in self.rule1_project.keys():
            for rule_date_str in self.datetime_check:
                for hostname in self.rule_hostname:
                    for rule1_index in self.rule1_index:
                        filename = rule1_file_pattern.format(rule1_project_keys = rule1_project_keys,
                                                             rule1_project_values = self.rule1_project[
                                                                 rule1_project_keys],
                                                             rule_date_str1 = rule_date_str.format(self.rule_date_str1),
                                                             rule_date_str2 = rule_date_str.format(self.rule_date_str2),
                                                             hostname = hostname, rule1_index = rule1_index)
                        check_filename[filename] = "/".join(filename.split("/")[0:-1])
        return check_filename
    
    def _str_filename_rule2(self):
        check_filename = dict()
        # 构造rule2 "/log/{appids_values}/rawlog/{rule_date_str1}/{appids_keys}.log-{rule_date_str3}-{hostname}"
        rule2_file_pattern = monitor_hdfs_log_config.rule2_file_pattern
        for rule_date_str in self.datetime_check:
            for appids_keys in self.appids.keys():
                for hostname in self.rule_hostname:
                    filename = rule2_file_pattern.format(appids_values = self.appids[appids_keys],
                                                         rule_date_str1 = rule_date_str.format(self.rule_date_str1),
                                                         appids_keys = appids_keys,
                                                         rule_date_str3 = rule_date_str.format(self.rule_date_str3),
                                                         hostname = hostname)
                    # print filename
                    check_filename[filename] = "/".join(filename.split("/")[0:-1])
        return check_filename
    
    def _str_filename_rule3(self):
        check_filename = dict()
        # 构造Rule3 "/data_warehouse/ods_origin.db/log_raw/key_day={rule_date_str1}/key_hour={rule_date_str4}/{appids_keys}.log-{rule_date_str3}-{hostname}"
        rule3_file_pattern = monitor_hdfs_log_config.rule3_file_pattern
        for rule_date_str in self.datetime_check:
            for appids_keys in self.appids.keys():
                for hostname in self.rule_hostname:
                    filename = rule3_file_pattern.format(rule_date_str1 = rule_date_str.format(self.rule_date_str1),
                                                         rule_date_str4 = rule_date_str.format(self.rule_date_str4),
                                                         appids_keys = appids_keys,
                                                         rule_date_str3 = rule_date_str.format(self.rule_date_str3),
                                                         hostname = hostname)
                    check_filename[filename] = "/".join(filename.split("/")[0:-1])
        return check_filename
    
    def _check_filename(self, check_filename, rule_name):
        no_found = list()
        # 取得字典中的HDFS PATH
        hdfs_path = list(set(check_filename.values()))
        hdfs_files = MyHdfs(hdfs_path).get_hdfs_info()
        for item in check_filename.keys():
            # check_full_filename = os.path.join(check_filename[item], item)
            check_full_filename = item
            if check_full_filename not in hdfs_files:
                is_match = False
                for pattern in monitor_hdfs_log_config.white_list_pattern:
                    match = re.search(pattern, item)
                    if match:
                        is_match = True
                if not is_match:
                    no_found.append(check_full_filename)
        
        if no_found:
            no_found_files = "\n".join(no_found)
            msg_error = "以下文件HDFS缺失 :\n %s" % no_found_files
            log_msg("no_found", msg_error, 2)
            mail_sub = "%sHDFS 有文件不存在！ " % rule_name
            send_alter_mail(sub = mail_sub, body = msg_error)
            return False
        else:
            msg_success = "未发现缺失的文件"
            log_msg("check", msg_success, 1)
            return True
    
    def check_workflows(self):
        # pdb.set_trace()
        check_rule1 = self._str_filename_rule1()
        # check_rule2 = self._str_filename_rule2()
        check_rule3 = self._str_filename_rule3()
        
        self._check_filename(check_rule1, "Rule1")
        # self._check_filename(check_rule2, "Rule2")
        self._check_filename(check_rule3, "Rule3")


def main():
    mylocal = MyLocal()
    mylocal.check_workflows()


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
