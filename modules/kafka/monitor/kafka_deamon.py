# -*- coding: utf-8 -*-

import redis
import commands
import logging
import sys
import pdb

redis_host = '10.255.130.7'
port = 6380
db = 1


def run_cmd(cmd):
    msg = "Starting run: %s " % cmd
    logMsg("run_cmd", msg, 1)
    output = commands.getoutput(cmd)
    return output


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


def return_redis_lag(topic):
    r = redis.Redis(host=redis_host, port=port, db=db)
    lasttime = r.get("lasttime")
    key = "%s_%s" % (topic, lasttime)
    values = r.hget(key, 'lag')
    return values


def restart_kafka(topic):
    get_pid_cmd = "jps -lvm|grep %s" % topic
    output = run_cmd(get_pid_cmd)
    pid = output.split()[0]
    kill_cmd = "kill -9 %s" % pid
    run_cmd(kill_cmd)
    start_cmd = "sh /opt/ai/kafkaIO/shell/%s.sh" % topic
    import os
    os.system(start_cmd)



def main():
    topics = sys.argv[1].split(',')
    for topicname in topics:
        lag = return_redis_lag(topicname)

        if int(lag) != 0:
            restart_kafka(topicname)
        else:
            msg="redis OK"
            logMsg("check_redis",msg,1)


if __name__ == "__main__":
    main()
