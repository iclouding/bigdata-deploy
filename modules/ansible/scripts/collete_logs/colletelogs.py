# -*- coding: utf-8 -*-
import logging
import subprocess
import sys
import os
import datetime


def run_cmd(cmd):
    msg = "Starting run: %s " % cmd
    logMsg("run_cmd", msg, 1)
    cmdref = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error_info = cmdref.communicate()
    if not output:
        if isinstance(error_info, list) or isinstance(error_info, tuple):
            error_info = error_info[0]
        msg = "RUN %s ERROR,error" % cmd
        logMsg("run_cmd", msg, 2)
        return 1, cmd
    else:
        msg = "run %s success" % cmd
        logMsg("cmd", msg, 1)
        # print "Run Success!!"
        return 0, cmd


def logMsg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = None
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


def get_local_path(path):
    dir_ = os.listdir(path)
    full_dir_ = "%s/%s" % (path, dir_[0])
    if os.path.isdir(full_dir_):
        return full_dir_
    else:
        return False


def return_day(days):
    str_day = (datetime.date.today() - datetime.timedelta(days)).strftime("%y%m%d")
    return str_day


def main():
    if len(sys.argv) == 1:
        days = 1
    else:
        days = int(sys.argv[1])
    str_day = return_day(days)
    dest_path_first = "/data/backups/api_nginx_log/moretv_recommend"
    dest_path = "%s/%s" % (dest_path_first, str_day)
    mkdir_cmd = "mkdir -p %s" % dest_path
    run_cmd(mkdir_cmd)

    for i in range(1, 7):
        source_path_suffix = "/data/databack/Moretv/recommended/nginx0%d/log/" % i

        source_path = get_local_path("%s%s" % (source_path_suffix, str_day))
        if not source_path:
            msg = "%s 不规范" % ("%s%s" % (source_path_suffix, str_day))
            logMsg("check", msg, 2)
            raise KeyError
        source_filename = "_data_logs_nginx---rec.tvmore.com.cn.access.log-%s.gz" % ("20%s" % str_day)
        dest_filename = "%s%s" % (source_path_suffix.replace("/", "_"), source_filename)
        cmd = " cp %s/%s %s/%s" % (source_path, source_filename, dest_path, dest_filename)
        print cmd
        run_cmd(cmd)


if __name__ == "__main__":
    main()
