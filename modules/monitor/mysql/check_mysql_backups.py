# -*- coding: utf-8 -*-
import logging
import commands
import json
import requests
import socket
import re
import sys
import arrow
import os

# checkfiles like appsvr/130-7/db/171030-02/10.255.130.7/db_171030-02.tar.gz

SEND_TO = "peng.tao@whlaey.cn"
BASE_PATH = '/data/databack'
HOSTLIST = ("bigdata-extsvr-db_bi1", "bigdata-extsvr-db_bi2", "bigdata-appsvr-130-7", "bigdata-cmpt-128-25",
            "bigdata-extsvr-sdkconfsvr1",)


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
    logger.removeHandler(hdlr)


def send_alter_mail(sub, body):
    mail_content = dict()
    mail_content["sub"] = sub
    mail_content["content"] = body
    mail_content["sendto"] = SEND_TO
    mail_url = 'http://10.19.15.127:5006/mail/api/v1.0/send'

    heads = {'content-type': 'application/json'}
    r = requests.post(url=mail_url, headers=heads, data=json.dumps(mail_content))
    if r.status_code == 200:
        log_msg("send_alter_mail", "send mail success", 1)
    else:
        err_msg = "send mail failed ,output was %s" % r.content
        log_msg("send_alter_mail", err_msg, 2)


def check_logs(check_time):
    # hostname bigdata-appsvr-130-7
    # check step 1 check db_171030-02.tar.gz size
    # check step 2 tail -1 /data/databack/bigdata/appsvr/130-7/db/171030-02/10.255.130.7/back_db.log
    for check_host in HOSTLIST:
        host_split = check_host.split('-')
        str_filter = "{0}-{1}-".format(host_split[0], host_split[1])
        hostname_change = "{0}/{1}/{2}".format(host_split[0], host_split[1], check_host.lstrip(str_filter))

        check_path = "{base_path}/{hostname_change}/db/{check_time}-02/".format(base_path=BASE_PATH,
                                                                                hostname_change=hostname_change,
                                                                                check_time=check_time)
        ip_layer = os.listdir(check_path)[0]
        full_path = "{0}/{1}".format(check_path, ip_layer)
        if not os.path.isdir(full_path):
            error_msg = "path %s no found " % full_path
            log_msg("check_logs", error_msg, 2)
            raise RuntimeError("%s" % error_msg)
        check_files = "db_{0}-02.tar.gz ".format(check_time)
        if not os.path.isfile("{0}/{1}".format(full_path, check_files)) or os.path.getsize(
                "{0}/{1}".format(full_path, check_files)) < (1000 * 1000 * 10):
            error_msg = "备份文件过小"
            log_msg("check_logs", error_msg, 2)
            sub = "%s 备份文件过小" % socket.gethostname()
            body = "备份文件过小或不存在，请检查"
            send_alter_mail(sub, body)
            raise RuntimeError(error_msg)

        # 检查log文件最后一行是否有"completed OK"
        check_files02 = "{0}/back_db.log".format(full_path)
        if not os.path.isfile(check_files02):
            error_msg = "back_db.log 文件不存在"
            log_msg("check_log", error_msg, 2)
            sub = "%s db log 文件不存在" % socket.gethostname()
            send_alter_mail(sub, error_msg)
            raise RuntimeError(error_msg)

        check_cmd = "tail -1 {0}/back_db.log".format(full_path)
        status, output = commands.getstatusoutput(check_cmd)
        if status == 0:
            patten = "completed OK"
            if re.search(patten, output):
                return True
            else:
                error_msg = "检查DB备份日志关键词失败"
                sub = "%s 检查日志关键词失败" % socket.gethostname()
                log_msg("check_logs", error_msg, 2)
                send_alter_mail(sub, error_msg)
                raise RuntimeError(error_msg)
        else:
            error_msg = "读取日志失败"
            sub = "%s 读取日志失败" % socket.gethostname()
            log_msg("check_logs", error_msg, 2)
            send_alter_mail(sub, error_msg)
            raise RuntimeError(error_msg)


def main():
    if len(sys.argv) == 2:
        check_time = arrow.utcnow().shift(days=-1).to("Asia/Shanghai").format("YYMMDD")
    elif len(sys.argv) == 3:
        check_time = sys.argv[1]
    else:
        raise KeyError("PLS input datatime which need check")

    check_logs(check_time)


if __name__ == "__main__":
    try:
        main()
    except:
        import StringIO, traceback

        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        # info = sys.exc_info()
        msg_errror = "mysql表锁检查脚本运行异常 %s" % message
        mail_sub = "%s mysql表锁检查脚本运行异常" % socket.gethostname()
        send_alter_mail(sub=mail_sub, body=msg_errror)

