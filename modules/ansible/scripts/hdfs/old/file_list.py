#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json
import pdb

def _get_local_list(path):
    check_dir = path
    check_files = []
    local_list = dict()
    if os.path.isdir(check_dir):
        for root, dirs, files in os.walk(check_dir):
            for file_one in files:
                if file_one:  # self.param[0] == "all" or file.split(".")[-1] in self.param:
                    filename = os.path.join(root, file_one)
                    local_list[filename] = os.path.getsize(filename)
    return local_list

def _write_file(filename,data):
    with open(filename,'a+') as f:
        f.write(data)

    return True

def main():
    pdb.set_trace()
    path=os.path.abspath('.')
    file_list=_get_local_list(path)
    j_data=json.dumps(file_list,indent=1)
    filename='%s.log'%path
    _write_file(filename,j_data)



if __name__=='__main__':
    main()
