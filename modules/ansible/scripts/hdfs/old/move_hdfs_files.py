#!/usr/bin/python
# -*- coding: utf-8 -*-
import commands
import sys
import os



def initlog():
    import logging
    logger = None
    logger = logging.getLogger()
    hdlr = logging.FileHandler("default.log")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return [logger,hdlr]

def logMsg( fun_name, err_msg,level ):
    message = fun_name + ':'+err_msg
    logger,hdlr = initlog()
    logger.log(level ,message )
    hdlr.flush()
    logger.removeHandler( hdlr )#网络上的实现基本为说明这条语句的使用和作用

def run_cmd(cmd):
    (status, result)=commands.getstatusoutput(cmd)
    if status !=0:
        msg="cmd :%s failed"%cmd
        logMsg("run_cmd",msg,2)
        print result
        sys.exit(1)
    else:
        success_msg="Run cmd:%s success \n "%cmd
        print success_msg
        return result

def write_data(file,data):
    with open(file,'w') as f:
        f.write(data)

def get_hdfs_list(path):
    cmd="hadoop fs -ls %s/*.bz2"%path
    files_list=list()
    hdfs_list = run_cmd(cmd)
    for i  in range(len(hdfs_list.split('\n'))):
        n_list=list()
        if i >0:
            n_list=(hdfs_list.split('\n')[i].split()[4],hdfs_list.split('\n')[i].split()[7])
            files_list.append(n_list)
    return files_list

def check_local_size(file):
    local_size=os.path.getsize(file)
    return local_size

def change_hdfs_name(file):
    newfile="%s.%s"%(file,'download')
    change_cmd="hadoop fs -mv %s %s"%(file,newfile)
    run_cmd(change_cmd)
    return True

def scp_file(file):

    scp_cmd="scp %s root@10.10.1.13:/data1/%s"%(file,file)
    run_cmd(scp_cmd)
    del_cmd="rm -f %s"%file
    run_cmd(del_cmd)
    return True


def check_local_list(suffix,list):
    for line in list:
        size,file=line
        local_file="%s/%s"%(suffix,file)
        if not os.path.isfile(local_file):
            msg="local file not found "
            logMsg("local",msg,2)
            break
        local_size=check_local_size(local_file)
        if int(size)==int(local_size):
            if scp_file(local_file):
                change_hdfs_name(file)
            else:
                msg="scp files faild %s"%file
                logMsg("scp",msg,2)
        else:
            msg="check files size error file was %s"%local_file
            logMsg("check_size",msg,2)



def main():
    path=sys.argv[1]
    list=get_hdfs_list(path)
    check_local_list("/backup/hdfs/",list)

    #get hdfs list,write info to file ,for in files ,get hdfs to local,check local size ,rename hdfs,move to other

if __name__=="__main__":
    main()