# -*- coding: utf-8 -*-
# System modules
import time
import logging
import sys
import commands
from datetime import timedelta, datetime
import os
import datetime
import hashlib


def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
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


class MyGaoshen():
    def __init__(self, domain, work_day, output):
        self.domain = domain
        self.work_day = work_day
        self.output = output
        self.dw = {}
        if self.domain == "mediags.moguv.com":
            self.dw['user_id'] = u'253'.replace('\'', '')
        else:
            self.dw['user_id'] = u'185'.replace('\'', '')
        self.dw['dtype'] = u'vod'.replace('\'', '')
        self.dw['logtype'] = u'access'.replace('\'', '')
        now_date = datetime.datetime.now().strftime("%Y%m%d")
        self.key = 'gaosheng_' + now_date

    def down(sele):
        cmd = self.get_cdn_url()
        status, out = commands.getstatusoutput(cmd)
        if status == 0:
            print "{0} run success，out was {1}".format(cmd, out)
        else:
            msg = "{0} run failed ,out was {1}".format(cmd, out)
            log_msg("run", msg, 2)

    def get_cdn_url(self):
        sortdict = sorted(self.dw.iteritems(), key=lambda d: d[0])
        md5str = ''
        for v in sortdict:
            md5str += str(v[1])
        md5str = md5str + self.key
        # print 'before:', md5str
        md5 = hashlib.md5(md5str.encode('utf-8')).hexdigest()
        # print 'after:', md5
        get_url = "http://portal.gosun.com/api/downloads_log?user_id=%s&vhost=%s&day=%s&logtype=%s&dtype=%s&sign=%s" % (
            self.dw['user_id'], self.dw['domain'], self.dw['day'], self.dw['logtype'], self.dw['dtype'], md5)
        # print get_url
        files = "%s_%s.gz" % (self.domain, self.work_day)
        cmd = "wget  -c '%s' -O %s/%s" % (get_url, self.output, files)
        return cmd



def upLogs2Hdfs():
    yesterday = (datetime.date.today() -
                 datetime.timedelta(1)).strftime("%Y%m%d")
    yesterday_format2 = yesterday.strftime('%Y%m%d')
    baseLocal = '/data/down_gaoshen/'
    hdfsDir = "/log/cdn/%s" % yesterday_format2
    currLocal = "%s/%s" % (baseLocal, yesterday_format2)
    cmd = "su - spark -c 'hadoop fs -put -f %s /log/cdn'" % currLocal
    (returncode, out) = commands.getstatusoutput(cmd)
    if returncode == 0:
        rm_cmd = "su - spark -c 'hadoop fs -rm %s/*/*.list'" % hdfsDir
        commands.getoutput(rm_cmd)
        log_msg("rmHdfs", "run cmd %s" % rm_cmd, 1)
        log_msg("up2Hdfs", "Up2Hdfs success", 1)
        return True
    else:
        msg = "run %s Failed,output : %s" % (cmd, out)
        log_msg("upLogs2Hdfs", msg, 2)
        raise KeyError


def run_azkaban():
    project = 'ods_etl_cdn_log'
    flow = 'microsoft_cdn_end'
    cmd = "/bin/sh azkaban_run.sh %s %s" % (project, flow)
    (code, output) = commands.getstatusoutput(cmd)
    if code == 0:
        log_msg("run_azkaban", "Starting gaoshen_cdn workflow success", 1)
        return True
    else:
        msg = "run gaoshen_cdn Failed ,message was %s" % output
        log_msg("run_azkaban", msg, 2)
        raise KeyError


def main():
    domain_name = ['media-wr.moguv.com', 'media2-wr.moguv.com',
                  'media-wr.mairx.com', 'p2p-wr.mairx.com']
    out_path = "/data/down_gaoshen/"
    if len(sys.argv) == 1:
        work_day = (datetime.date.today() -
                    datetime.timedelta(1)).strftime("%Y%m%d")
    elif len(sys.argv == 2):
        work_day = sys.argv[1]
    else:
        raise Exception("输入格式错误，请检查参数!", 2)

    for domain_one in domain_name:
        g=MyGaoshen(domain_one,work_day,out_path)
        g.down()

    upLogs2Hdfs()
    run_azkaban()


if __name__ == "__main__":
    main()
