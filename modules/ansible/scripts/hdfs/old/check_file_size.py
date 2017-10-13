#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import json


def txt2dict(path):
    with open(path,'r') as f:
        z=json.load(f)
    return z

def write_data(filename,data):
    with open(filename,'a+') as f:
        f.write(data)


def main():
    path1 = sys.argv[1]
    path2 = sys.argv[2]
    data1=txt2dict(path1)
    data2=txt2dict(path2)


    for i in range(len(data1.keys())):
        if not data2.get(('/home/data1/13/'+data1.keys()[i]),None):
            file1='nofound.log'
            msg1="%s not in desc,desc info was %s \n"%(data1.keys()[i],str(data2.get(('/home/data1/13/'+data1.keys()[i]),None)))
            write_data(file1,msg1)
        if data2.get(('/home/data1/13/'+data1.keys()[i]),None) != data1[data1.keys()[i]]:
            filename = 'check_list_err.log'
            msg="%s values is diff \n"%data1.keys()[i]
            write_data(filename,msg)

if __name__=='__main__':
    main()



