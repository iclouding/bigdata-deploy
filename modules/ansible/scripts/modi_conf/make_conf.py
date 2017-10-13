#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import subprocess
import os
import sys
import pdb
import socket
import re


def initlog():
    import logging
    logger = None
    logger = logging.getLogger()
    log_name = sys.argv[0].split(".")[0] + ".log"
    hdlr = logging.FileHandler(log_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return [logger, hdlr]


def logMsg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger, hdlr = initlog()
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)  # 网络上的实现基本为说明这条语句的使用和作用


def get_host():
    host_name = socket.gethostname()
    return host_name


def get_section_values(sections, filename):
    cf = ConfigParser.SafeConfigParser()
    cf.read(filename)
    configDataSection = cf.sections()
    returnData = {}

    if sections in configDataSection:
        _list = cf.items(sections)
        for _key, _value in _list:
            returnData[_key] = _value
    else:
        print "[ERROR] %s is not in config files,PLS check it %s" % (sections, filename)
        msg_info = "===%s: Get info Failed!!===" % sections
        logMsg("get_config", msg_info, 2)
        return False
    return returnData


def _run_cmd(cmd):
    print "Starting run: %s " % cmd
    cmdref = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out = cmdref.stdout.read()
    print "run cmd  output " + out
    data = cmdref.communicate()
    if cmdref.returncode == 0:
        msg = "Run %s success \n" % cmd
        msg = msg + data[0]
        print(msg)
        return True
    else:
        msg = "[ERROR] Run %s False \n" % cmd
        msg = msg + data[1]
        logMsg("Run", msg, 2)
        return False
def escape_string(data,souce,dest):
    souce_list=souce.split(',')
    dest_list=dest.split(',')
    for i in range(len(souce_list)):
        data=data.replace(souce_list[i],dest_list[i])
    return data



def match_modi_file(host_name, filename):
    cf = ConfigParser.SafeConfigParser()
    cf.read(filename)
    sections = cf.sections()
    match_all = list()
    for section in sections:
        section = escape_string(section,'{,}','[,]')
        pattern = re.compile(section.split(':')[0])
        match_ = pattern.match(host_name)

        if match_:
            match_all.append(section)
    for match_one in match_all:
        modi_file = match_one.split(":")[-1]
        match_one=escape_string(match_one,'[,]','{,}')
        values = get_section_values(match_one, filename)

        if modi_file_run(modi_file, values):
            return True
        else:
            msg = "Modi file %s Error" % modi_file
            logMsg("Modi_file", msg, 2)


def modi_file_run(file, data):
    for item in data.keys():
        modi_key = "{{%s}}" % item
        # sed -i 's#{{server.1}}#pt1:2888:3888#g' /opt/zookeeper/conf/zoo.cfg
        cmd = "sed -i 's#%s#%s#g' %s" % (modi_key, data[item], file)
        print "Run_Cmd was : %s" % cmd
        _run_cmd(cmd)


def main():
    host_name = get_host()
    filename = os.path.join(os.path.abspath('.'), sys.argv[1])
    match_modi_file(host_name, filename)

    # for file in need_modi_data.keys():
    #     if not modi_file(need_modi_data[file]["file"], need_modi_data[file]["values"]):
    #         raise "Modi file error"


if __name__ == '__main__':
    main()
