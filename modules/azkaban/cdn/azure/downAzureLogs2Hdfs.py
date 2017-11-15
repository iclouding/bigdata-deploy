# -*- coding: utf-8 -*-
# System modules
import time
import logging
import sys
import commands
from datetime import timedelta, datetime
import os

from azure.storage.blob import BlockBlobService

account = 'whaleycndlog'
key = 'lMkPgMc+XpZQZHmM174vji0LKSvusmjVOpxGh60qxsU1srolGYG/pbhgxgygW7SDE/6EkfqVMUOUxpKvGnV1ng=='


# blobname = 'cdn-access-logs'


def read_files(filename):
    with open(filename, 'r') as f:
        data = f.read().strip()
    return data


def write_files(filename, data):
    with open(filename, 'a+') as f:
        f.write(data)
        f.write("\n")


def logMsg(fun_name, err_msg, level):
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


class Myazure():
    def __init__(self, account, key):
        self.account = account
        self.key = key
        self.endpoint = 'core.chinacloudapi.cn'
        self.blockblobservice = BlockBlobService(account_name=self.account, account_key=self.key,
                                                 endpoint_suffix=self.endpoint)

    def downAzureLogs(self, blobname, filename, currDir, checkFilename):
        print '%s:Downloading:' % filename
        downFilename = '%s/%s' % (currDir, filename)

        self.blockblobservice.get_blob_to_path(blobname, filename, downFilename)
        write_files(checkFilename, filename)
        # logMsg("downFiles", "Download files %s  to %s success" % (filename, downFilename), 1)

    def list_blobs(self, blobname, values):
        blobs = self.blockblobservice.list_blobs(blobname, prefix=values)
        data = list()
        for blob in blobs:
            data.append(blob.name)
            print blob.name
        return data


def mydownAzureLogs(domainName):
    # Set up some global variables
    myblobs = Myazure(account, key)

    yesterday = datetime.today() + timedelta(-1)
    yesterday_format = yesterday.strftime('%Y-%m-%d')
    yesterday_format2 = yesterday.strftime('%Y%m%d')

    for item in domainName:
        values = "%s-CST-%s" % (item, yesterday_format)
        # 创建下载目录
        baseDir = '/data/down/'
        currDir = "%s%s/%s" % (baseDir, yesterday_format2, item)

        cmd = "mkdir -p %s" % currDir
        commands.getoutput(cmd)
        allFilename = "%s/%s.list" % (currDir, values)
        checkFilename = "%s/%s_check.list" % (currDir, values)
        blobname = item.replace(".", "-")

        if os.path.isfile(allFilename):
            dataAll = read_files(allFilename).split("\n")
        else:
            files = myblobs.list_blobs(blobname, values)
            write_files(allFilename, "\n".join(files))
            dataAll = files

        if len(dataAll) != 24:
            data_all_msg = "logs != 24 ,pls check"
            logMsg("get_list", data_all_msg, 2)
            # raise KeyError

        if os.path.isfile(checkFilename):
            dataDown = read_files(checkFilename).split("\n")
        else:
            cmd = "touch %s" % checkFilename
            commands.getoutput(cmd)
            dataDown = list()

        downfiles = list(set(dataAll).difference(set(dataDown)))

        for filename in downfiles:
            myblobs.downAzureLogs(blobname, filename, currDir, checkFilename)

        msg = "Down azure logs about %s success!" % yesterday_format
        logMsg("downAzureLogs", msg, 1)


def upLogs2Hdfs():
    yesterday = datetime.today() + timedelta(-1)
    yesterday_format2 = yesterday.strftime('%Y%m%d')
    baseLocal = '/data/down/'
    hdfsDir = "/log/cdn/%s" % yesterday_format2
    currLocal = "%s/%s" % (baseLocal, yesterday_format2)
    cmd = "su - spark -c 'hadoop fs -put -f %s /log/cdn'" % currLocal
    (returncode, out) = commands.getstatusoutput(cmd)
    if returncode == 0:
        rm_cmd = "su - spark -c 'hadoop fs -rm %s/*/*.list'" % hdfsDir
        commands.getoutput(rm_cmd)
        logMsg("rmHdfs", "run cmd %s" % rm_cmd, 1)
        logMsg("up2Hdfs", "Up2Hdfs success", 1)
        return True
    else:
        msg = "run %s Failed,output : %s" % (cmd, out)
        logMsg("upLogs2Hdfs", msg, 2)
        raise KeyError


def run_azkaban():
    project = 'ods_etl_cdn_log'
    flow = 'microsoft_cdn_end'
    cmd = "/bin/sh azkaban_run.sh %s %s" % (project, flow)
    (code, output) = commands.getstatusoutput(cmd)
    if code == 0:
        logMsg("run_azkaban", "Starting gaoshen_cdn workflow success", 1)
        return True
    else:
        msg = "run gaoshen_cdn Failed ,message was %s" % output
        logMsg("run_azkaban", msg, 2)
        raise KeyError


def main():
    domainName = ['media-wr.moguv.com', 'media2-wr.moguv.com', 'media-wr.mairx.com']
    mydownAzureLogs(domainName)
    upLogs2Hdfs()
    run_azkaban()


if __name__ == "__main__":
    main()

