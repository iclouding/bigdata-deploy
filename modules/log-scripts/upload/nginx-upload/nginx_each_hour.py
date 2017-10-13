# -*- coding: utf-8 -*-
"""
功能：
1.1 每个小时0分0秒，对Nginx正在写的日志进行重命名，完成后执行nginx -s reopen，进行日志的滚动
1.2 滚动完成后，需要将滚动生成的上个小时的日志，其中几个特别的日志，根据appId上传至指定目录下
1.3 每个小时滚动产生的所有日志上传是数仓ODS原始层的指定目录下
1.4 上传失败时，需要重试一次。如果重试继续失败，则发送邮件
要求：
1.1 /data/logs/nginx目录下的所有文件都需要一起完成重命名，然后执行nginx -s reopen进行文件滚动，所以重命名的过程应该尽可能短
1.2 将特定几个appId的文件上传到指定目录
1.3 所有文件上传至数仓ODS原始层目录，并hive add partition语句
1.4 如果上传成功，将上传成功文件列表记录在特定文件中。如果重试上传失败，发送告警邮件，同时需要有比较简单的手动补偿机制
1.5 整个过程需要记录日志，包括在什么时间点处理了哪些日志文件，对比校验的结果等，以便后续排查问题
1.6 由于磁盘空间有限，需要将已上传成功且超过时效范围的文件转移到其他目录，并有另外的脚本执行定时删除动作
1.7 每天00:30，对昨天的文件进行一次，HDFS的完整比对校验

	本地目录：/data/logs/nginx
	需要上传到特定hdfs目录的文件命名规则：#{appId}.log-#{yyyyMMddHH}-#{hostname}(示例：boikgpokn78sb95kjhfrendoepkseljn.log-2017090610-bigdata-extsvr-log2)
	文件匹配规则：boikgpokn78sb95k.*.log-*-{hostname}
	特定hdfs目录规则：/log/#{appId}/rawlog/#{yyyyMMdd}

	本地目录下所有文件都上传至数仓ODS原始层（以下简称“原始层”）
	文件匹配规则：bigdata-extsvr
	原始层HDFS规则：/data_warehouse/ods_origin.db/log_raw/key_day=#{yyyyMMdd}/key_hour=#{HH}
	hive sql 语句：/opt/hive/bin/hive -e "alter table ods_origin.log_raw add partition(key_day='#{yyyyMMdd}',key_hour='#{HH}') location '/data_warehouse/ods_origin.db/log_raw/key_day=#{yyyyMMdd}/key_hour=#{HH}'"

工作流程
    1、nginx日志（匹配规则，*.log）在代码运行时进行滚动（多个MV完成后一次性reopen ）
    2、按规则查找当前路径下命名符合规则且时间区间匹配的文件
    3、与HDFS已存在的文件进行匹配，返回需上传的文件列表
    # 4、期间发现本地文件为0（-rw-r--r-- 1 nobody root            0 9月   8 15:00 weixinlog.moretv.log-2017090815-bigdata-extsvr-log3），或与hdfs大小不一致的文件，发送报警邮件
    5、按列表上传文件，且对上传的文件大小进行匹配，如有文件不存在，或大小不一致的情况，发送报警邮件，重传一次
    6、执行hive add partition语句
    7、需要将已上传成功且超过时效范围的文件转移到其他目录

q1:特定appid 列表
q2:nginx日志的匹配规则,是否有黑白名单？例如access.log没有切割
q3:切割规则-#{yyyyMMddHH}-#{hostname}
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
import nginx_each_hour_config


def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = logging.getLogger()
    base_name = nginx_each_hour_config.logs
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
    mysub = "Nginx_upload %s " % socket.gethostname()
    mail_content["sub"] = mysub + sub
    mail_content["content"] = body
    mail_content["sendto"] = nginx_each_hour_config.sendto
    mail_url = 'http://10.19.15.127:5006/mail/api/v1.0/send'
    
    heads = {'content-type': 'application/json'}
    r = requests.post(url = mail_url, headers = heads, data = json.dumps(mail_content))
    if r.status_code == 200:
        log_msg("send_alter_mail", "send mail success", 1)
    else:
        err_msg = "send mail failed ,output was %s" % r.content
        log_msg("send_alter_mail", err_msg, 2)


def run_cmd(cmd):
    dry_run = nginx_each_hour_config.debug
    output = ""
    if dry_run:
        status = 0
    else:
        (status, output) = commands.getstatusoutput(cmd)
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
        self.appids = nginx_each_hour_config.appids
        self.datetime = arrow.utcnow().to('Asia/Shanghai').shift(hours = -1).format("YYYYMMDDHH")
    
    def _list_local_files(self):
        all_local_files = list()
        all_local = os.listdir(self.path)
        for item in all_local:
            if os.path.isfile(os.path.join(self.path, item)):
                all_local_files.append(item)
        return all_local_files
    
    def _split_filename_hdfs(self, filename):
        # "boikgpokn78sb95ktmsc1bnkfipphckl.log-2017090815-bigdata-extsvr-log3"  ('boikgpokn78sb95ktmsc1bnkfipphckl', '2017090815', 'bigdata-extsvr-log3') appid-time-hostname
        # weixinlog.moretv.log-2017090815-bigdata-extsvr-log3  ('weixinlog.moretv', '2017090815', 'bigdata-extsvr-log3')
        
        pattern = "([\w\.]+)\.log-%s-([\w\-]+)" % self.datetime
        match_values = re.match(pattern, filename)
        if match_values:
            appid = match_values.group(1)
            if appid in self.appids.keys():
                return appid
            else:
                msg_error = "appid %s no found! " % appid
                log_msg("_split_filename_hdfs", msg_error, 2)
                return None
        else:
            return None
    
    def _split_filename_ods(self, filename):
        """
        列出所有符合ODS规则的文件列表规则为hostname与本地相符
        
        :param filename: 文件列表
        :return: hostname
        """
        # "boikgpokn78sb95ktmsc1bnkfipphckl.log-2017090815-bigdata-extsvr-log3"  ('boikgpokn78sb95ktmsc1bnkfipphckl', '2017090815', 'bigdata-extsvr-log3') appid-time-hostname
        # weixinlog.moretv.log-2017090815-bigdata-extsvr-log3  ('weixinlog.moretv', '2017090815', 'bigdata-extsvr-log3')
        pattern = "([\w\.]+)\.log-%s-([\w\-]+)" % self.datetime
        match_values = re.match(pattern, filename)
        if match_values:
            hostname = match_values.group(2)
            if hostname == socket.gethostname():
                return True
        return False
    
    def _str_hdfs_path(self, filename):
        """
        按本地文件名计算出HDFS对应的上传路径
        :param filename: 本地文件名
        :return: HDFS上传路径
        """
        appid = self._split_filename_hdfs(filename)
        #    /log/#{appId}/rawlog/#{yyyyMMdd}
        if appid:
            hdfs_path = "/log/{appid}/rawlog/{datetime}".format(appid = self.appids[appid],
                                                                datetime = self.datetime[0:8])
            return hdfs_path
        else:
            return False
    
    def _str_ods_path(self, filename):
        """
        按本地文件名计算出HDFS对应的上传路径
        :param filename: 本地文件名
        :return: HDFS上传路径
        """
        
        match = self._split_filename_ods(filename)
        #    /log/#{appId}/rawlog/#{yyyyMMdd}
        if match:
            # /data_warehouse/ods_origin.db/log_raw/key_day =  # {yyyyMMdd}/key_hour=#{HH}
            hdfs_path = "/data_warehouse/ods_origin.db/log_raw/key_day={dateday}/key_hour={datehour}".format(
                    dateday = self.datetime[0:8], datehour = self.datetime[8:10])
            return hdfs_path
        else:
            return False
    
    def return_match_files_hdfs(self):
        """
        用于匹配本地路径下符合文件名规则及时间的文件列表
        输入参数本地路径名
        返回本地文件列表（不带路径的文件名及文件大小）,本地文件远程HDFS对应关系
        """
        # 获得匹配规则的文件列表
        all_files = self._list_local_files()
        local_files_info = dict()
        local_hdfspath = dict()
        for item in all_files:
            # print "current filename was %s" % item
            appid = self._split_filename_hdfs(item)
            if appid:
                local_hdfspath[item] = self._str_hdfs_path(item)
                # 获得列表对应的文件信息
                local_files_info[item] = os.path.getsize(os.path.join(self.path, item))
        return local_files_info, local_hdfspath
    
    def return_match_files_ods(self):
        """
        用于匹配本地路径下符合文件名规则及时间的文件列表
        输入参数本地路径名
        返回本地文件列表（不带路径的文件名及文件大小）,本地文件远程HDFS对应关系
        """
        # 获得匹配规则的文件列表
        all_files = self._list_local_files()
        local_files_info = dict()
        local_ods_path = dict()
        for item in all_files:
            match = self._split_filename_ods(item)
            if match:
                local_ods_path[item] = self._str_ods_path(item)
                # 获得列表对应的文件信息
                local_files_info[item] = os.path.getsize(os.path.join(self.path, item))
        return local_files_info, local_ods_path


class LogPoll():
    """
    用于对本地日志文件进行轮询操作
    目标文件时间戳为当前时间-1小时
    切割前判断目标文件是否存在，如存在则不处理该文件，并发报警邮件
    规则为mtvkidslog.moretv.log 滚动为mtvkidslog.moretv.log-2017091109-bigdata-extsvr-log1
    输入为文件列表（带路径）
    输出为操作完成True或失败（发送报警邮件，错误信息写入日志）
    """
    
    def __init__(self, path):
        self.path = path
        self.base_files = self._get_logs_filename()
        self.poll_files = self._poll_filename()
    
    def _match_nginx_logs(self, filename):
        """
        匹配需滚动的nginx日志文件
        如log.moretv.log
        :return:True or False
        """
        pattern = "([\w\.]+)\.log$"
        match_values = re.match(pattern, filename)
        if match_values:
            # appid = match_values.groups(1)
            return True
        else:
            return False
    
    def _get_logs_filename(self):
        all_item = os.listdir(self.path)
        need_poll_files = list()
        for item in all_item:
            if os.path.isfile(os.path.join(self.path, item)):
                if self._match_nginx_logs(item):
                    need_poll_files.append(item)
        return need_poll_files
    
    def _poll_filename(self):
        poll_file = list()
        for filename in self.base_files:
            new_filename = "{filename}-{datetime}-{hostname}".format(filename = filename, datetime = arrow.utcnow().to(
                    'Asia/Shanghai').shift(hours = -1).format("YYYYMMDDHH"), hostname = socket.gethostname())
            poll_file.append(new_filename)
        return poll_file
    
    def _check_before_cmd(self):
        """
        文件切割前检查目标文件是否存在，如存在发送报警邮件，并在列表中清理该文件
        :return: True or False
        """
        all_files = os.listdir(self.path)
        poll_remove = list()
        base_remove = list()
        for i in range(len(self.poll_files)):
            if self.poll_files[i] in all_files:
                sub = "日志切割前检查发现异常"
                msg_error = "目标文件%s已存在，请人工介入处理，该文件暂不切割！" % self.base_files[i]
                send_alter_mail(sub = sub, body = msg_error)
                log_msg("poll_before_check", msg_error, 2)
                poll_remove.append(self.poll_files[i])
                base_remove.append(self.base_files[i])
        
        if poll_remove:
            for item in poll_remove:
                self.poll_files.remove(item)
        
        if base_remove:
            for item in base_remove:
                self.base_files.remove(item)
    
    def poll_log(self):
        self._check_before_cmd()
        pool_cmd = ""
        for i in range(len(self.poll_files)):
            cmd_sub = "mv {filename}  {poll_filename} && ".format(
                    filename = os.path.join(self.path, self.base_files[i]),
                    poll_filename = os.path.join(self.path, self.poll_files[i]))
            pool_cmd += cmd_sub
        pool_cmd += " /opt/openresty/nginx/sbin/nginx -s reopen"
        # pool_cmd += "echo success"
        status, output = commands.getstatusoutput(pool_cmd)
        if status == 0:
            msg_success = "run cmd %s success" % pool_cmd
            log_msg("poll_log", msg_success, 1)
            return True
        else:
            msg_failed = "run %s failed: %s" % (pool_cmd, output)
            log_msg("poll_log", msg_failed, 2)
            sub = "日志切割执行失败"
            send_alter_mail(sub = sub, body = msg_failed)
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


class HdfsCommands():
    def __init__(self, local_path):
        self.retry = nginx_each_hour_config.retry
        self.local_path = local_path
        # 获得本地需上传文件列表
        self.local_info, self.local_hdfs = MyLocal(self.local_path).return_match_files_hdfs()
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
            if self._up_commnads():
                if self._check_after_up():
                    return True
                else:
                    msg_error = "本地路径%s上传失败，重传" % self.local_path
                    log_msg("up2hdfs", msg_error, 2)
            
            else:
                i += 1
                print "重传%s" % self.local_path
        
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
                # if int(os.path.getsize(os.path.join(self.local_path, item))) != int(new_hdfs_info[item]):
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
        new_hdfs_info = MyHdfs(self.hdfs_paths).get_hdfs_info()
        # 检查列表是否存在空文件，是否有与 HDFS大小不一致的文件
        for item in self.local_info.keys():
            
            # 如果HDFS文件存在，且与本地大小一致
            if item in new_hdfs_info.keys():
                if int(self.local_info[item]) == int(new_hdfs_info.get(item, 0)):
                    del self.local_info[item]
                    del self.local_hdfs[item]
                
                # 如果HDFS文件存在，且与本地大小不一致
                else:
                    # int(local_info[item]) != int(hdfs_info.get(item, 0)):
                    msg_err = "HDFS 文件大小不一致：Filename {filename} ，LocalSize {local_size} ,HdfsSize {hdfs_size}".format(
                            filename = item, local_size = self.local_info[item], hdfs_size = new_hdfs_info.get(item, 0))
                    log_msg("nginx_local2hdfs", msg_err, 2)
                    mail_sub = "HDFS 本地与HDFS大小不一致,请人工介入"
                    send_alter_mail(sub = mail_sub, body = msg_err)
                    del self.local_info[item]
                    del self.local_hdfs[item]


class OdsCommands():
    def __init__(self, local_path):
        self.retry = nginx_each_hour_config.retry
        self.local_path = local_path
        # 获得本地需上传文件列表
        self.local_info, self.local_hdfs = MyLocal(self.local_path).return_match_files_ods()
        # 获得HDFS路径下所有文件信息
        self.hdfs_paths = list(set(self.local_hdfs.values()))
        self.hdfs_info = MyHdfs(self.hdfs_paths).get_hdfs_info()
    
    def up2ods(self):
        """
        上传本地文件到HDFS，且进行检查，如失败重传1次
        输入:local_info dict,本地文件及大小
        输入：local_hdfs dict:本地文件及上传路径
        :return: True OR False
        """
        i = 1
        while i < self.retry:
            self._get_upload_list_ods()
            if self._up_commnads():
                if self._check_after_up():
                    return True
                else:
                    msg_error = "本地路径%s上传失败，重传" % self.local_path
                    log_msg("up2hdfs", msg_error, 2)
            
            else:
                i += 1
                print "重传%s" % self.local_path
        
        msg_error = "ODS 上传%s连续失败，请人工介入" % self.local_path
        mail_sub = "ODS 连续上传失败"
        send_alter_mail(sub = mail_sub, body = msg_error)
        log_msg("up2ods", msg_error, 2)
        return False
    
    def hive_add_partition(self):
        # 根据上传ODS的路径清单，获得需要hive 添加的2个datetime参数
        # hdfs_path like /data_warehouse/ods_origin.db/log_raw/key_day=#{yyyyMMdd}/key_hour=#{HH}'
        up_ods_datetime = list()
        for item in list(set(self.local_hdfs.values())):
            pattern = "/data_warehouse/ods_origin.db/log_raw/key_day=(\d{8})/key_hour=(\d{2})"
            match_values = re.match(pattern, item)
            if match_values:
                match_date = (match_values.group(1), match_values.group(2))
                up_ods_datetime.append(match_date)
            
            # 如果没匹配上，即没文件需要上传，记录日志，返回
            if not up_ods_datetime:
                msg_not_match = "没有需要操作的文件: %s" % ",".join(self.hdfs_paths)
                log_msg("hive_add_partition", msg_not_match, 1)
            else:
                for date_day, date_hour in up_ods_datetime:
                    hive_cmd = "su - spark -c \"/opt/hive/bin/hive -e \\\"alter table ods_origin.log_raw add if not exists partition(key_day='{date_day}',key_hour='{date_hour}') location '/data_warehouse/ods_origin.db/log_raw/key_day={date_day}/key_hour={date_hour}'\\\"\"".format(
                            date_day = date_day, date_hour = date_hour)
                    if not run_cmd(hive_cmd):
                        sub = "Hive add partition失败"
                        msg_error = "Hive add partition失败 ，请人工介入"
                        send_alter_mail(sub = sub, body = msg_error)
                        log_msg("hive_add_partition", msg_error, 2)
                    else:
                        log_msg("hive_add_partition", "hive_add_partition 操作完成 hour %s " % str(date_hour), 1)
    
    def _check_after_up(self):
        new_hdfs_info = MyHdfs(self.hdfs_paths).get_hdfs_info()
        for item in self.local_info.keys():
            if item not in new_hdfs_info.keys():
                msg_err = "%s HDFS未找到" % item
                log_msg("_check_after_up", msg_err, 2)
                return False
            if int(self.local_info[item]) != int(new_hdfs_info[item]):
                # if int(os.path.getsize(os.path.join(self.local_path, item))) != int(new_hdfs_info[item]):
                msg_err = "%s 大小不一致, Local %s ,HDFS %s" % (item, str(self.local_info[item]), str(new_hdfs_info[item]))
                log_msg("_check_after_up", msg_err, 2)
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
    
    def _get_upload_list_ods(self):
        # 检查列表是否存在空文件，是否有与 HDFS大小不一致的文件
        new_hdfs_info = MyHdfs(self.hdfs_paths).get_hdfs_info()
        for item in self.local_info.keys():
            # 如果文件存在，且与本地大小一致
            if item in new_hdfs_info.keys():
                if int(self.local_info[item]) == int(new_hdfs_info.get(item, 0)):
                    del self.local_info[item]
                    del self.local_hdfs[item]
                
                # 如果文件存在，且与本地大小不一致
                else:
                    # int(local_info[item]) != int(hdfs_info.get(item, 0)):
                    msg_err = "文件大小不一致：Filename {filename} ，LocalSize {local_size} ,HdfsSize {hdfs_size}".format(
                            filename = item, local_size = self.local_info[item], hdfs_size = new_hdfs_info.get(item, 0))
                    log_msg("_get_upload_list_ods", msg_err, 2)
                    mail_sub = "本地与ODS大小不一致,请人工介入"
                    send_alter_mail(sub = mail_sub, body = msg_err)
                    del self.local_info[item]
                    del self.local_hdfs[item]


def nginx_local2hdfs(local_path):
    # 将本地文件上传到HDFS，且进行检查
    if HdfsCommands(local_path).up2hdfs():
        return True
    return False


def nginx_local2ods(local_path):
    # local 上传到ODS
    datetime = arrow.utcnow().to('Asia/Shanghai').shift(hours = -1).format("YYYYMMDDHH")
    touch_ods_status(datetime, "start")
    my_ods = OdsCommands(local_path)
    if my_ods.up2ods():
        touch_ods_status(datetime, "end")
        my_ods.hive_add_partition()
        return True
    return False


def nginx_poll(local_path):
    import datetime
    starttime = datetime.datetime.now()
    if not LogPoll(local_path).poll_log():
        return False
    endtime = datetime.datetime.now()
    msg_time = "切割操作执行时间: %s microseconds" % str((endtime - starttime).microseconds)
    print msg_time
    log_msg("nginx_poll", msg_time, 1)
    return True


def touch_ods_status(datetime, status):
    filename = "{datetime}_{hostname}_{status}".format(datetime = datetime, hostname = socket.gethostname(),
                                                       status = status)
    touch_cmd = 'su - spark -c "hadoop fs -touchz {hdfs_path}/{filename}"'.format(
            hdfs_path = nginx_each_hour_config.upload_status_path, filename = filename)
    status, output = commands.getstatusoutput(touch_cmd)
    if status == 0:
        print "touch cmd was %s" % touch_cmd
        return True
    else:
        msg_errror = "touch ods status Failed ,cmd was %s ,output was %s" % (touch_cmd, output)
        log_msg("touch_ods_status", msg_errror, 2)
        return False


def main():
    local_path = nginx_each_hour_config.local_paths
    if nginx_poll(local_path):
        msg_success = "日志切割执行完成！"
        log_msg("main", msg_success, 1)
        import time
        time.sleep(10)
        if nginx_local2ods(local_path):
            msg_success = "日志上传ODS步骤执行成功"
            log_msg("main", msg_success, 1)
            # if nginx_local2hdfs(local_path):
            #     msg_success = "日志上传HDFS步骤执行成功"
            #     log_msg("main", msg_success, 1)
            # else:
            #     msg_error = "日志上传HDFS执行出错"
            #     log_msg("main", msg_error, 2)
            #     mail_sub = "日志上传HDFS出错"
            #     send_alter_mail(sub = mail_sub, body = msg_error)
        else:
            msg_error = "日志上传ODS执行出错"
            log_msg("main", msg_error, 2)
            mail_sub = "日志上传ODS出错"
            send_alter_mail(sub = mail_sub, body = msg_error)
    else:
        msg_error = "日志切割执行出错"
        log_msg("main", msg_error, 2)
        # mail_sub = "日志切割出错"
        # send_alter_mail(sub = mail_sub, body = msg_error)
        raise RuntimeError("日志切割出错")


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
