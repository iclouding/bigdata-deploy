# -*- coding: utf-8 -*-
import logging
import sys
import time
import commands
import os
import json
import requests
import pdb


def logMsg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = logging.getLogger()
    #logname = sys.argv[0] + '.log'
    logname='/data/logs/hive/hiveManager.log'
    hdlr = logging.FileHandler(logname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)


def _runCmd(cmd):
    (status, output) = commands.getstatusoutput(cmd)
    if status != 0:
        errMsg = "Run cmd %s Failed ,output was %s" % (cmd, output)
        logMsg("runcmd", errMsg, 2)
        raise KeyError
    else:
        msg = "Run cmd %s success!" % cmd
        logMsg("runcmd", msg, 1)
        return True


def getHostname():
    import socket
    return socket.gethostname()


def sendAlterMail():
    hostname = getHostname()
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    mailContent = dict()
    mailContent["sub"] = "%s Hive 重启失败报警" % hostname
    mailContent["content"] = " %s %s Hive 一小时未找到重启的机会" % (hostname, now)
    mailContent["sendto"] = "lian.kai@whaley.cn,peng.tao@whaley.cn"
    mailUrl = 'http://10.19.15.127:5006/mail/api/v1.0/send'
    # sendMailCMD = "curl -i -H 'Content-Type: application/json' -X POST -d '%s'  %s" % (json.dumps(mailContent), mailUrl)
    # _runCmd(sendMailCMD)
    heads = {'content-type': 'application/json'}
    r = requests.post(url=mailUrl, headers=heads, data=json.dumps(mailContent))
    if r.status_code == 200:
        logMsg("sendmail", "send mail success", 1)
    else:
        errMsg = "send mail failed ,output was %s" % r.content
        logMsg("sendmail", errMsg, 2)


def readFileModeTime(filename):
    if os.path.isfile(filename):
        return os.path.getmtime(filename)
    else:
        return 0


def checklogInfo(filename):
    baseTime = time.time()
    while True:
        fileModeTime = readFileModeTime(filename)
        if int(time.time() - fileModeTime) > 300:
            return True
        else:
            if int(time.time() - baseTime) > 3600:
                sendAlterMail()
                msg = "试图重启Hive进程等待1小时失败"
                logMsg("checkLog", msg, 2)
                raise RuntimeError
            time.sleep(60)
            continue


def mvLogName(filename):
    timeStr = time.strftime("%Y%m%d%H%M%S", time.localtime())
    newFilename = "%s-$%s.log" % (filename[0:-4], timeStr)
    mvCmd = "mv %s %s" % (filename, newFilename)
    commands.getoutput(mvCmd)


def restartHive():
    msg = "Hive service restart "
    logMsg("restart", msg, 1)
    stopCmd = "ps -ef | grep -i hiveserver2 | grep -v grep | awk '{print $2}' | xargs kill -9"
    startCmd = "su - hadoop -c 'nohup /opt/hive/bin/hiveserver2 > /data/logs/hive/hiveserver2.log 2>&1 &'"
    commands.getoutput(stopCmd)
    time.sleep(5)
    _runCmd(startCmd)


def main():
    logname = '/data/logs/hive/hiveserver2.log'
    if checklogInfo(logname):
        mvLogName(logname)
        restartHive()


if __name__ == "__main__":
    main()
