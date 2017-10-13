#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
from optparse import OptionParser
import pdb

def initlog():
    import logging
    logger = None
    logger = logging.getLogger()
    hdlr = logging.FileHandler("check_hdfs.log")
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
    msg= "Starting run: %s "%cmd
    logMsg("run_cmd",msg,1)
    cmdref = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output,error_info = cmdref.communicate()
    if error_info:
        msg= "RUN %s ERROR,error info:  ",(cmd,error_info)
        logMsg("run_cmd",msg,2)
        return False
    else:
        #print "Run Success!!"
        return output


class HdfsFiles():
    def __init__(self,path):
        self.path=path
        self.rename_shell="/root/script/hdfs_%s_rename.sh"%self.path.replace('/','_')
        self.error_file="/root/script/error_%s_path.log"%self.path.replace('/','_')
        self.parquet_list="/root/script/%s_parquet.list"%self.path.replace('/','_')


    def _get_hdfs_list(self):
        cmd="hadoop fs -ls -R %s"%self.path[18:]
        cmd_list=run_cmd(cmd)
        hdfs_list=dict()
        for line in cmd_list.split("\n"):
            if line and len(line.split())==8:
                hdfs_list[line.split()[7]]=line.split()[4]
        return hdfs_list


    def _struc_mv_hdfs(self,path):
        newfile = "%s.%s" % (path, 'download')
        change_cmd = "hadoop fs -mv %s %s " % (path, newfile)
        return change_cmd

    def _wite_file(self,path,data):
        with open(path,'a+') as f:
            f.write(data)
            f.write("\n")


    def _get_local_list(self):
        check_dir=self.path
        check_files = []
        local_list=dict()
        if os.path.isdir(check_dir):
            for root, dirs, files in os.walk(check_dir):
                for file_one in files:
                    if file_one:#self.param[0] == "all" or file.split(".")[-1] in self.param:
                        filename=os.path.join(root,file_one)
                        local_list[filename]=os.path.getsize(filename)

                        #check_files.append(os.path.join(root, file_one))
        else:
            msg= "%s is not a path ,pls check it " % dir
            logMsg("check_local_dir",msg,2)
        return local_list

    def check_local(self):
        local_dict=self._get_local_list()
        hdfs_dict=self._get_hdfs_list()

        for local_path in local_dict.keys():
            self._check_local(local_dict,hdfs_dict,local_path)

    def _check_local(self,local_dict,hdfs_dict,local_path):
        hdfs_size = hdfs_dict.get(local_path[18:], None)
        if not hdfs_size:
            msg = "%s not found in hdfs" % local_path[18:]
            self._wite_file(self.error_file, local_path[18:])
            logMsg("check", msg, 2)
            return False
        if int(hdfs_size) != int(local_dict.get(local_path,0)):
            msg = "%s size is diff with local " % local_path[18:]
            self._wite_file(self.error_file, local_path[18:])
            logMsg("check", msg, 2)
            return False
        elif os.path.split(local_path)[-1].split('.')[-1] == "parquet":
            self._wite_file(self.parquet_list, local_path[18:])
            return True
        else:
            cmd = self._struc_mv_hdfs(local_path[18:])
            self._wite_file(self.rename_shell, cmd)
            return True


def main():
    usage  = '''
    %prog -s get -p path
    %prog -s put -p path -m * -d 10.10.2.25 -r False
    '''
    parser = OptionParser(usage)
    parser.add_option("-p","--path",type="string",default=False,dest="path",
                      help="path")

    (options,args) = parser.parse_args()

    # if not options.func or not options.path:
    #     parser.print_usage
    # parser.error("arguments defined error!")

    f=HdfsFiles(options.path)
    f.check_local()

if __name__=="__main__":
    main()