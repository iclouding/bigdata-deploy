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
    hdlr = logging.FileHandler("hdfs_command.log")
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

#
# def run_cmd(cmd):
#     msg = "Starting run: %s " % cmd
#     logMsg("run_cmd", msg, 1)
#     cmdref = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#     output, error_info = cmdref.communicate()
#     if error_info:
#         if isinstance(error_info, list) or isinstance(error_info,tuple):
#             error_info = "error"
#         msg = "RUN %s ERROR,error info:  %s"% (cmd, error_info)
#         logMsg("run_cmd", msg, 2)
#         return False
#     else:
#         # print "Run Success!!"
#         return output


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
    def __init__(self,path,destip,param,rename):
        self.path=path
        self.param=param.split(',')
        self.destip=destip
        self.rename=rename

    def put_files(self):
        files=self._check_local_path()

        for one_file in files:
            if self._get_hdfs_info(one_file)==str(self._get_local_info(one_file)):
                self._scp_remot(one_file)
                self._mv_hdfs(one_file)
                self._rm_local_files(one_file)
            else:
                msg="%s File size diff with hdfs "%one_file
                logMsg("check_size",msg,2)


    def get_files(self):

        LocalDir='/backup/hdfs'+self.path
        local_mkdir="mkdir -p %s"%LocalDir
        run_cmd(local_mkdir)
        #for param_one in self.param:
        cmd="hadoop fs -get %s/* %s/ "%(self.path,LocalDir)
        run_cmd(cmd)
        return True

    def _check_local_path(self):
        dir=self.path
        check_files = []
        if os.path.isdir(dir):
            for root, dirs, files in os.walk(dir):
                for file in files:
                    if self.param[0] == "all" or file.split(".")[-1] in self.param:
                        check_files.append(os.path.join(root, file))
        else:
            msg= "%s is not a path ,pls check it " % dir
            logMsg("check_local_dir",msg,2)
        return check_files

    def _get_hdfs_info(self,filename):
        cmd="hadoop fs -ls %s"%filename[12:]
        file_info=run_cmd(cmd).split()[4]
        return file_info

    def _get_local_info(self,filename):
        local_size = os.path.getsize(filename)
        return local_size

    def _rm_local_files(self,filename):
        del_cmd = "sudo rm -f %s" % filename
        run_cmd(del_cmd)
        return True

    def _scp_remot(self,filename):

        dir="/data1"+os.path.split(filename)[0]

        create_dir='ssh root@%s "mkdir -p %s"'%(self.destip,dir)
        run_cmd(create_dir)
        scp_cmd="scp %s root@%s:/data1/%s"%(filename,self.destip,filename)
        run_cmd(scp_cmd)
        return True

    def _mv_hdfs(self,filename):
        if self.rename.lower()=="true":
            filename=filename[12:]
            newfile = "%s.%s" % (filename, 'download')
            change_cmd = "hadoop fs -mv %s %s" % (filename, newfile)
            run_cmd(change_cmd)
        return True


def main():
    usage  = '''
    %prog -s get -p path
    %prog -s put -p path -m * -d 10.10.2.25 -r False
    '''
    parser = OptionParser(usage)
    parser.add_option("-p","--path",type="string",default=False,dest="path",
                      help="path")
    parser.add_option("-m","--param",type="string",default='all',dest="param",
                      help="like .bz2,.*")
    parser.add_option("-s","--function",type="string",default="put",dest="func",
                      help="put or get")
    parser.add_option("-d","--dest ip",type="string",default="10.10.1.13",dest="destip",
                      help="dest ip in 10.10.1.13,10.10.2.25")
    parser.add_option("-r","--rename",type="string",default="True",dest="rename",
                      help="rename file")

    (options,args) = parser.parse_args()

    # if not options.func or not options.path:
    #     parser.print_usage
    # parser.error("arguments defined error!")


    if options.func=="put":
        f=HdfsFiles(options.path,options.destip,options.param,options.rename)
        f.put_files()
    elif options.func=="get":
        f=HdfsFiles(options.path,options.destip,options.param,options.rename)
        f.get_files()
    else:
        raise "Must choose put or get"

if __name__=="__main__":
    main()