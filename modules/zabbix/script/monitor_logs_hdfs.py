# -*- coding: utf-8 -*-
import sys

sys.path.append("..")
import common
from  mmail import mailBase
import os
import time
import socket
import ConfigParser
import pdb
import redis


# /log/medusa/rawlog/20170314

def send_alter_bymail():
    pass


class HdfsInfo():
    def __init__(self, data, hdfs_path):
        # self.files_suffix = data['files_suffix']
        self.r = redis.Redis(host=data['redis_host'], port=data['port'], db=data['db'])
        self.expirted = data['expired']
        self.host_suffix = data['host_suffix']
        self.time_suffix = time.strftime("%Y-%m-%d-%H", time.localtime())
        self.hdfs_path = hdfs_path

    def check_workflow(self):

        is_alter = False
        # 检查redis中miss_files字段是否有值，写入操作时间及结果，1=True
        check_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.r.set('monitor_logs_time', check_time)
        is_true, miss_file = self.get_local_miss_files()
        common.write_file_josn('/tmp/miss_file.log', miss_file)
        if is_true:
            self.r.set('miss_local_file', 1)

            is_alter = True
        else:
            self.r.set('miss_local_file', 0)

        local_file_info = self.get_local_info()
        hdfs_file_info = self.get_hdfs_info()
        miss_hdfs_file_key = "miss_hdfs_file_%s" % check_time
        diff_size_key = "diff_size_%s" % check_time
        diff_files = dict()
        miss_hdfs_file = list()
        for key in local_file_info.keys():
            if key not in hdfs_file_info.keys():
                self.r.rpush(miss_hdfs_file_key, key)
                miss_hdfs_file.append(key)
                is_alter = True

            if local_file_info.get(key, None) != hdfs_file_info.get(key, None):
                diff_files[key] = [local_file_info.get(key, None), hdfs_file_info.get(key, None)]
        if diff_files.keys():
            self.r.hmset(diff_size_key, diff_files)
            is_alter = True
        common.write_file_josn('/tmp/miss_hdfs_file.log', miss_hdfs_file)
        common.write_file_josn('/tmp/diff_size.log', diff_files)

        if is_alter:
            msg = "find error alter mail will send"
            common.logMsg("sendmail", msg, 1)
            mail_dict = dict()
            mail_dict['mail_host'] = "smtp.exmail.qq.com"  # 设置服务器
            mail_dict['mail_user'] = "peng.tao@whaley.cn"  # 用户名
            mail_dict['mail_pswd'] = "tel7206324"  # 口令
            mail_dict['mail_rece'] = list()
            mail_dict['mail_rece'].append("peng.tao@whaley.cn")
            mail_dict['mail_rece'].append("lian.kai@whaley.cn")
            mail_dict['mail_rece'].append('feng.jin@whaley.cn')

            m = mailBase(**mail_dict)
            sub = "日志检查报警邮件"
            content = "本地与HDFS日志文件存在异常，详见附件！"
            attachs = ("/tmp/miss_file.log", "/tmp/miss_hdfs_file.log", "/tmp/diff_size.log")
            m.sendMail(sub, content, 'plain', 'utf-8', *attachs)
        else:
            msg = "miss not found"
            common.logMsg("check", msg, 1)

    def _get_local_files_info(self, hostname):

        files_info_key = "bigdata_monitor_log_%s_%s" % (hostname, self.time_suffix)
        local_files = self.r.hgetall(files_info_key)
        return local_files

    def get_local_info(self):
        local_file_info = dict()
        for i in range(1, int(self.host_suffix)):
            hostname = 'bigdata-extsvr-log%d' % i
            local_files = self._get_local_files_info(hostname)
            for key in local_files.keys():
                new_key = key.split('/')[-1]
                # 过滤路径
                local_file_info[new_key] = local_files[key]
        return local_file_info

    def get_hdfs_info(self):
        hdfs_file_info = dict()
        check_path = list()

        for path in self.hdfs_path:
            time_now = time.strftime("%Y%m%d", time.localtime())
            time_yesterday = time.strftime("%Y%m%d", time.localtime(time.time() - (3600 * 24)))
            check_path.append('%s%s' % (path, time_now))
            check_path.append('%s%s' % (path, time_yesterday))

        for hdfs_path in check_path:
            cmd = 'hadoop fs -ls -R %s' % hdfs_path
            is_run, out = common.run_cmd(cmd)
            if is_run:
                if out:
                    for line in out.split('\n'):
                        line_values = line.split()
                        if len(line_values) == 8:
                            filename = line_values[7].split('/')[-1]
                            hdfs_file_info[filename] = line_values[4]
        return hdfs_file_info

    def get_local_miss_files(self):
        miss_files_key = "bigdata_monitor_miss_log_%s" % self.time_suffix
        if self.r.exists(miss_files_key):
            miss_files = self.r.hgetall(miss_files_key)
            return 1, miss_files
        else:
            return 0, None


def main():
    config_file = sys.argv[1]

    sections = common.return_section(config_file)
    common_data = common.get_section_values('common', config_file)
    sections.remove('common')
    alter_info = dict()
    hdfs_path_l = list()
    for section in sections:
        data = common.get_section_values(section, config_file)
        hdfs_path = data.get('hdfs_path', None)
        hdfs_path_l.append(hdfs_path)
    check = HdfsInfo(common_data, hdfs_path_l)
    check.check_workflow()


if __name__ == "__main__":
    main()
