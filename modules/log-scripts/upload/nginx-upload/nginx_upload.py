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
import sys
import nginx_upload_config


def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = logging.getLogger()
    base_name = nginx_upload_config.logs
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
    mail_content["sendto"] = nginx_upload_config.sendto
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


def nginx_local2hdfs(local_path):
    # local 上传到 HDFS
    # 获得本地路径下所有文件
    all_files = _list_local_files(local_path)
    up_list_nocomp_hdfs = list()
    # 获得需要补传的时间列表
    up_date = _get_datetime_list()
    appids = nginx_upload_config.appids
    # 按预定正则和时间过滤列表，获得需上传的文件
    for filename in all_files:
        (appid, file_time, hostname) = _split_ods_filename(filename)
        if appid in appids.keys() and file_time in up_date:
            up_list_nocomp_hdfs.append(filename)
    
    # 基于需上传列表，生成本地文件大小及本地-HDFS路径对应的字典
    local_info = dict()  # 未与HDFS比对的本地文件及大小表
    local_hdfs = dict()  # 未与HDFS比对的本地文件及HDFS路径对应表
    for item in up_list_nocomp_hdfs:
        local_info[item] = os.path.getsize(os.path.join(local_path, item))
        local_hdfs[item] = _get_local_files_hdfs_path(item)
    hdfs_info_all = MyHdfs(list(set(local_hdfs.values()))).get_hdfs_info()
    # 与HDFS比对，找到HDFS不存在的文件:
    local_hdfs_need_up = dict()
    for filename in local_info.keys():
        if filename not in hdfs_info_all.keys():
            local_hdfs_need_up[filename] = _get_local_files_hdfs_path(filename)
        elif int(local_info[filename]) != int(hdfs_info_all[filename]):  # 如果本地与HDFS大小不一致，报警通知人工处理，该文件不在上传
            mail_sub = "上传前检查发现本地与HDFS 大小不一致"
            msg_error = "%s 文件大小不一致：LOCAL %s HDFS %s" % (
                filename, str(local_info(filename)), str(hdfs_info_all[filename]))
            send_alter_mail(sub = mail_sub, body = msg_error)
        else:
            print "%s 本地与远程一致" % filename
    
    # 本地文件都已上传到HDFS，将本地检查列表返回给删除操作
    if not local_hdfs_need_up:
        msg_zero = "未能找到需要上传的文件"
        log_msg("nginx_local2hdfs", msg_zero, 1)
        return True, local_info.keys()
    
    # 本地文件都已上传到HDFS，将本地检查列表返回给删除操作
    if not local_hdfs_need_up:
        msg_zero = "HDFS未能找到需要上传的文件"
        log_msg("nginx_local2hdfs", msg_zero, 1)
        return True, local_info.keys()
    # 上传文件
    if up2hdfs(local_path, local_hdfs_need_up):
        # 检查上传,找到本地与HDFS一致的文件（可删除），本地与HDFS均存在但大小 不一致的文件（报警）
        hdfs_info_after_up = MyHdfs(list(set(local_hdfs_need_up.values()))).get_hdfs_info()
        file_need_mv = list()
        file_nofound = list()
        file_diff_size = list()
        for filename in local_hdfs_need_up.keys():
            if filename not in hdfs_info_after_up.keys():  # 发现未上传文件
                file_nofound.append(filename)
            elif int(local_info[filename]) != int(hdfs_info_after_up[filename]):  # 发现大小不同的文件
                file_diff_size.append(filename)
            else:
                file_need_mv.append(filename)
        
        if file_nofound:
            file_info = "\n".join(file_nofound)
            msg_error = "文件未上传到HDFS：\n %s" % file_info
            mail_sub = "HDFS上传异常，文件未找到"
            send_alter_mail(sub = mail_sub, body = msg_error)
            return False, None
        
        if file_diff_size:
            file_diff = "\n".join(file_diff_size)
            msg_error = "文件大小与HDFS不一致：\n %s" % file_diff
            mail_sub = "HDFS上传异常，文件大小异常"
            send_alter_mail(sub = mail_sub, body = msg_error)
            return False, None
        
        if file_need_mv:
            return True, file_need_mv
        else:
            msg_info = "已检查本地及HDFS未发现需要删除的文件"
            log_msg("up_hdfs", msg_info, 1)
            return True, None
    
    else:
        msg_error = "执行上传命令返回错误"
        log_msg("nginx_local2ods", msg_error, 2)
        mail_sub = "HDFS 上传失败"
        send_alter_mail(sub = mail_sub, body = msg_error)
        return False, None


def remove_up_files(local_path, file_need_mv):
    # 删除已上传的文件
    for item in file_need_mv:
        mv_cmd = "mv {sour_filename} {dest_path}".format(sour_filename = os.path.join(local_path, item),
                                                         dest_path = nginx_upload_config.backup_path)
        if not run_cmd(mv_cmd):
            return False
    remove_cmd = "cd %s && rm -f *-log*" % nginx_upload_config.backup_path
    if not run_cmd(remove_cmd):
        return False
    return True


def _list_local_files(path):
    all_local_files = list()
    all_local = os.listdir(path)
    for item in all_local:
        if os.path.isfile(os.path.join(path, item)):
            all_local_files.append(item)
    return all_local_files


def _get_datetime_list():
    begin_hours = nginx_upload_config.hours
    step = nginx_upload_config.step
    up_date = list()
    for i in range(int(step)):
        up_date.append(arrow.utcnow().to('Asia/Shanghai').shift(hours = -(int(begin_hours) + i)).format("YYYYMMDDHH"))
    return up_date


def _get_local_files_ods_path(file):
    (appid, datetime, hostname) = _split_ods_filename(file)
    # /data_warehouse/ods_origin.db/log_raw/key_day =  # {yyyyMMdd}/key_hour=#{HH}
    hdfs_path = "/data_warehouse/ods_origin.db/log_raw/key_day={dateday}/key_hour={datehour}".format(
            dateday = datetime[0:8], datehour = datetime[8:10])
    return hdfs_path


def _get_local_files_hdfs_path(file):
    (appid, datetime, hostname) = _split_ods_filename(file)
    appids = nginx_upload_config.appids
    # /data_warehouse/ods_origin.db/log_raw/key_day =  # {yyyyMMdd}/key_hour=#{HH}
    hdfs_path = "/log/{appid}/rawlog/{datetime}".format(appid = appids[appid], datetime = datetime[0:8])
    return hdfs_path


def _split_ods_filename(filename):
    # "boikgpokn78sb95ktmsc1bnkfipphckl.log-2017090815-bigdata-extsvr-log3"
    pattern = "([\w\.]+)\.log-(\d{10})-([\w\-]+)"
    match_values = re.match(pattern, filename)
    if match_values:
        appid = match_values.group(1)
        file_time = match_values.group(2)
        hostname = match_values.group(3)
    
    else:
        appid = None
        hostname = None
        file_time = None
    
    return (appid, file_time, hostname)


def up2hdfs(local_path, local_hdfs):
    # 按HDFS路径做聚合上传
    poly_hdfs_info = defaultdict(list)
    
    for items in local_hdfs.items():
        poly_hdfs_info[items[1]].append(items[0])
    
    for hdfs_path in poly_hdfs_info.keys():
        mkdir_hdfs_dir = "su - spark -c'/opt/hadoop/bin/hadoop fs -mkdir -p %s'" % hdfs_path
        if not run_cmd(mkdir_hdfs_dir):
            return False
        
        upload_files = " ".join(poly_hdfs_info[hdfs_path])
        print "开始上传文件:%s" % upload_files
        up2_hdfs_cmd = "su - spark -c'cd %s && /opt/hadoop/bin/hadoop fs -put %s %s'" % (
            local_path, upload_files, hdfs_path)
        if not run_cmd(up2_hdfs_cmd):
            return False
    return True


def hive_add_partition(local_hdfs):
    # 根据上传ODS的路径清单，获得需要hive 添加的2个datetime参数
    # hdfs_path like /data_warehouse/ods_origin.db/log_raw/key_day=#{yyyyMMdd}/key_hour=#{HH}'
    up_ods_datetime = list()
    for item in list(set(local_hdfs.values())):
        pattern = "/data_warehouse/ods_origin.db/log_raw/key_day=(\d{8})/key_hour=(\d{2})"
        match_values = re.match(pattern, item)
        if match_values:
            match_date = (match_values.group(1), match_values.group(2))
            up_ods_datetime.append(match_date)
        
        # 如果没匹配上，即没文件需要上传，记录日志，返回
        if not up_ods_datetime:
            msg_not_match = "没有需要操作的文件: %s" % ",".join(local_hdfs.values())
            log_msg("hive_add_partition", msg_not_match, 1)
        else:
            for date_day, date_hour in up_ods_datetime:
                """
                su - spark -c "/opt/hive/bin/hive -e \"alter table ods_origin.log_raw add if not exists partition(key_day='20170912',key_hour='18') location '/data_warehouse/ods_origin.db/log_raw/key_day=20170912/key_hour=18'\""
                """
                hive_cmd = "su - spark -c \"/opt/hive/bin/hive -e \\\"alter table ods_origin.log_raw add if not exists partition(key_day='{date_day}',key_hour='{date_hour}') location '/data_warehouse/ods_origin.db/log_raw/key_day={date_day}/key_hour={date_hour}'\\\"\"".format(
                        date_day = date_day, date_hour = date_hour)
            if not run_cmd(hive_cmd):
                sub = "Hive add partition失败"
                msg_error = "Hive add partition失败 ，请人工介入"
                send_alter_mail(sub = sub, body = msg_error)
                log_msg("hive_add_partition", msg_error, 2)
            else:
                log_msg("hive_add_partition", "hive_add_partition 操作完成 ", 1)


def touch_ods_status(datetime, status):
    filename = "{datetime}_{hostname}_{status}".format(datetime = datetime, hostname = socket.gethostname(),
                                                       status = status)
    touch_cmd = 'su - spark -c "hadoop fs -touchz {hdfs_path}/{filename}"'.format(
            hdfs_path = nginx_upload_config.upload_status_path, filename = filename)
    status, output = commands.getstatusoutput(touch_cmd)
    if status == 0:
        print "touch cmd was %s" % touch_cmd
        return True
    else:
        msg_errror = "touch ods status Failed ,cmd was %s ,output was %s" % (touch_cmd, output)
        log_msg("touch_ods_status", msg_errror, 2)
        return False


def nginx_local2ods(local_path):
    # local 上传到ODS
    
    # 获得本地路径下所有文件
    all_files = _list_local_files(local_path)
    
    up_list_nocomp_hdfs = list()
    
    # 获得需要补传的时间列表
    up_date = _get_datetime_list()
    
    # 按预定正则和时间过滤列表，获得需上传的文件
    for filename in all_files:
        (appid, file_time, hostname) = _split_ods_filename(filename)
        if hostname == socket.gethostname() and file_time in up_date:
            up_list_nocomp_hdfs.append(filename)
    
    # 基于需上传列表，生成本地文件大小及本地-HDFS路径对应的字典
    local_info = dict()  # 未与HDFS比对的本地文件及大小表
    local_hdfs = dict()  # 未与HDFS比对的本地文件及HDFS路径对应表
    for item in up_list_nocomp_hdfs:
        local_info[item] = os.path.getsize(os.path.join(local_path, item))
        local_hdfs[item] = _get_local_files_ods_path(item)
    hdfs_info_all = MyHdfs(list(set(local_hdfs.values()))).get_hdfs_info()
    # 与HDFS比对，找到HDFS不存在的文件:
    
    local_hdfs_need_up = dict()
    for filename in local_info.keys():
        if filename not in hdfs_info_all.keys():
            local_hdfs_need_up[filename] = _get_local_files_ods_path(filename)
        elif int(local_info[filename]) != int(hdfs_info_all[filename]):  # 如果本地与HDFS大小不一致，报警通知人工处理，该文件不在上传
            mail_sub = "上传前检查发现本地与HDFS 大小不一致"
            msg_error = "%s 文件大小不一致：LOCAL %s HDFS %s" % (
                filename, str(local_info[filename]), str(hdfs_info_all[filename]))
            send_alter_mail(sub = mail_sub, body = msg_error)
        else:
            print "%s 本地与远程一致" % filename
    
    # 本地文件都已上传到HDFS，将本地检查列表返回给删除操作
    if not local_hdfs_need_up:
        msg_zero = "ODS 未能找到需要上传的文件"
        log_msg("nginx_local2ods", msg_zero, 1)
        return True, local_info.keys()
    
    # 取得需上传文件的Datetime，touch start 文件在 upload_status_path
    upload_file_datetime_full = list()
    for item in local_hdfs_need_up.keys():
        _, filedate, _ = _split_ods_filename(item)
        upload_file_datetime_full.append(filedate)
    
    upload_file_datetime_begin = list(set(upload_file_datetime_full))
    for time in upload_file_datetime_begin:
        touch_ods_status(time, "start")
    
    # 上传文件
    
    if up2hdfs(local_path, local_hdfs_need_up):
        # 检查上传,找到本地与HDFS一致的文件（可删除），本地与HDFS均存在但大小 不一致的文件（报警）
        hdfs_info_after_up = MyHdfs(list(set(local_hdfs_need_up.values()))).get_hdfs_info()
        file_need_mv = list()
        file_nofound = list()
        file_diff_size = list()
        
        # hive add 操作
        
        hive_add_partition(local_hdfs_need_up)
        
        # 上传后文件检查
        for filename in local_hdfs_need_up.keys():
            if filename not in hdfs_info_after_up.keys():  # 发现未上传文件
                file_nofound.append(filename)
            elif int(local_info[filename]) != int(hdfs_info_after_up[filename]):  # 发现大小不同的文件
            #elif int(os.path.getsize(local_path, filename)) != int(hdfs_info_after_up[filename]):
                file_diff_size.append(filename)
            else:
                file_need_mv.append(filename)
        
        if file_nofound:
            for f_nofound in file_nofound:
                _, f_nofound_date, _ = _split_ods_filename(f_nofound)
                upload_file_datetime_begin.remove(f_nofound_date)
            file_info = "\n".join(file_nofound)
            msg_error = "文件未上传到HDFS：\n %s" % file_info
            mail_sub = "ODS上传异常，文件未找到"
            send_alter_mail(sub = mail_sub, body = msg_error)
            return False, None
        
        if file_diff_size:
            for f_diff_size in file_diff_size:
                _, f_diff_date, _ = _split_ods_filename(f_diff_size)
                upload_file_datetime_begin.remove(f_diff_date)
            file_diff = "\n".join(file_diff_size)
            msg_error = "文件大小与HDFS不一致：\n %s" % file_diff
            mail_sub = "ODS上传异常，文件大小异常"
            send_alter_mail(sub = mail_sub, body = msg_error)
            return False, None
        
        # 按过滤后的列表 在hdfs上创建ODS状态说明文件
        for upload_file_datetime_end in upload_file_datetime_begin:
            touch_ods_status(upload_file_datetime_end, "end")
        
        if file_need_mv:
            return True, file_need_mv
        else:
            msg_info = "已检查本地及HDFS未发现需要删除的文件"
            log_msg("up_ods", msg_info, 1)
            return True, None
    
    else:
        msg_error = "执行上传命令返回错误"
        log_msg("nginx_local2ods", msg_error, 2)
        mail_sub = "ODS 上传失败"
        send_alter_mail(sub = mail_sub, body = msg_error)
        return False, None


def main():
    local_path = nginx_upload_config.local_paths
    mv_files = list()
    
    if len(sys.argv) == 2:
        nginx_upload_config.hours = sys.argv[1]
    
    status_ods, file_list_ods = nginx_local2ods(local_path)
    if status_ods:
        msg_success = "日志上传ODS步骤执行成功"
        log_msg("main", msg_success, 1)
        if file_list_ods:
            mv_files.extend(file_list_ods)
        # status_hdfs, file_list_hdfs = nginx_local2hdfs(local_path)
        # if status_hdfs:
        #     msg_success = "日志上传HDFS步骤执行成功"
        #     log_msg("main", msg_success, 1)
        #     if file_list_hdfs:
        #         mv_files.extend(file_list_hdfs)
            
            if remove_up_files(local_path, list(set(mv_files))):
                log_msg("remove_up_files", "迁移路径%s下文件成功" % local_path, 1)
                log_msg("main", "所有操作执行成功", 1)
            else:
                log_msg("remove_up_files", "迁移路径%s下文件有错误" % local_path, 2)
                mail_sub = "删除过期文件出错"
                send_alter_mail(sub = mail_sub, body = "迁移路径%s下文件有错误" % local_path)
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
