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
    cmd="hadoop fs -ls %s/*.download"%path
    files_list=list()
    hdfs_list = run_cmd(cmd)
    for i  in range(len(hdfs_list.split('\n'))):
        n_list=list()
        if i >0:
            n_list=(hdfs_list.split('\n')[i].split()[4],hdfs_list.split('\n')[i].split()[7])
            files_list.append(n_list)
    return files_list


def change_hdfs_name(file):
    newfile=file[0:-9]
    change_cmd="hadoop fs -mv %s %s"%(file,newfile)
    print change_cmd
    #run_cmd(change_cmd)
    return True




def main():
    path=sys.argv[1]
    list_=get_hdfs_list(path)
    for _,files in list_:
        change_hdfs_name(files)



    #get hdfs list,write info to file ,for in files ,get hdfs to local,check local size ,rename hdfs,move to other

if __name__=="__main__":
    main()