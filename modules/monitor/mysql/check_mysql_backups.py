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
# deploy in 10.19.46.13  Platform-Ops-datacenter03

SEND_TO = "peng.tao@whaley.cn，lian.kai@whaley.cn"
BASE_PATH = '/data/databack'
HOSTLIST = ("bigdata-extsvr-db_bi2", "bigdata-appsvr-130-7", "bigdata-cmpt-128-25", "bigdata-extsvr-sdkconfsvr1",)


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
    log_msg("send", body, 2)

    heads = {'content-type': 'application/json'}
    r = requests.post(url=mail_url, headers=heads, data=json.dumps(mail_content))
    if r.status_code == 200:
        log_msg("send_alter_mail", "send mail success", 1)
    else:
        err_msg = "send mail failed ,output was %s" % r.content
        log_msg("send_alter_mail", err_msg, 2)


def run_cmd(cmd):
    print cmd
    status, output = commands.getstatusoutput(cmd)
    if status == 0:
        return output
    else:
        sub = "%s 执行CMD失败" % socket.gethostname()
        body = "执行输出为 %s" % output
        send_alter_mail(sub, body)
        raise RuntimeError(body)


def check_logs(check_time):
    # hostname bigdata-appsvr-130-7
    # check step 1 check db_171030-02.tar.gz size
    # check step 2 tail -1 /data/databack/bigdata/appsvr/130-7/db/171030-02/10.255.130.7/back_db.log
    for check_host in HOSTLIST:
        host_split = check_host.split('-')
        str_filter = "{0}-{1}-".format(host_split[0], host_split[1])
        rm_char_num = len(str_filter)

        hostname_change = "{0}/{1}/{2}".format(host_split[0], host_split[1], check_host[rm_char_num:])

        check_path = "{base_path}/{hostname_change}/db/{check_time}-*".format(base_path=BASE_PATH,
                                                                              hostname_change=hostname_change,
                                                                              check_time=check_time)

        files_size_cmd = "ls -an %s/*/*tar.gz |awk  '{print $5}'" % check_path

        file_last_row_cmd = "tail -1 %s/*/back_db.log" % check_path

        file_size = run_cmd(files_size_cmd)
        if not file_size or int(file_size) < (1000 * 1000 * 2):
            sub = "%s 检查备份文件过小" % socket.gethostname()
            body = "检查文件过小，文件路径为 %s" % check_path
            send_alter_mail(sub, body)
            raise RuntimeError(body)

        logs_status = run_cmd(file_last_row_cmd)
        patten = "completed OK"
        if not re.search(patten, logs_status):
            sub = "%s 日志检查不匹配" % socket.gethostname()
            body = "检查日志不匹配，输出为%s" % logs_status
            send_alter_mail(sub, body)
            raise RuntimeError(body)

        msg = "check %s success" % check_host
        log_msg("check", msg, 1)

    return True


def main():
    if len(sys.argv) == 1:
        check_time = arrow.utcnow().shift(days=-1).to("Asia/Shanghai").format("YYMMDD")
    elif len(sys.argv) == 2:
        check_time = sys.argv[1]
    else:
        raise KeyError("PLS input datatime which need check")

    if check_logs(check_time):
        log_msg("main", "检查备份成功", 1)


if __name__ == "__main__":
    try:
        main()
    except:
        import StringIO, traceback

        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        # info = sys.exc_info()
        msg_errror = "mysql备份检查脚本运行异常 %s" % message
        mail_sub = "%s mysql备份检查脚本运行异常" % socket.gethostname()
        send_alter_mail(sub=mail_sub, body=msg_errror)
