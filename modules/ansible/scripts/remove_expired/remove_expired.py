#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
新版本变动：
    1、查找待删除的文件支持正则
    2、加入参数del_dir=1,0(默认为0)，控制是否删除没有文件的目录
    3、文件是否过期按最后一次修改时间计算,将atime 改为ctime，后者是在写入文件、更改所有者、权限或链接设置时随 Inode 的内容更改而更改，即文件状态最后一次被改变的时间
    4、将过期判断由day改成house，实现更精细化的文件处理

'''
import os
import shutil
import re
import sys


def initlog():
    import logging
    logger = None
    logger = logging.getLogger()
    logname = sys.argv[0] + '.log'
    hdlr = logging.FileHandler(logname)
    # hdlr = logging.FileHandler("/data/scripts/default.log")
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


def getConfig(configName):
    import ConfigParser
    cf = ConfigParser.SafeConfigParser()
    cf.read(configName)
    configDataSection = cf.sections()
    returnData = []
    for sections_one in configDataSection:
        _dict = dict()
        _list = cf.items(sections_one)
        for _key, _value in _list:
            _dict[_key] = _value
        returnData.append(_dict)
    return returnData


def _remove(path, type='file'):
    try:
        if type == "file":
            msg = "RM file %s \n" % path
            logMsg("RM_file", msg, 1)
            #print "rm %s" % path
            os.remove(path)
        elif type == "dir":
            msg = "RM dir %s \n" % path
            logMsg("RM_dir", msg, 1)
            os.removedirs(path)
            #print "rm %s" % path
    except OSError as e:
        logMsg("OSError", str(e), 2)
    except:
        logMsg("remove_dir", 'unkonow', 2)


def _remove_all(path):
    import shutil
    # pdb.set_trace()
    msg = "RM dir %s \n" % path
    logMsg("RM_dir_all", msg, 1)
    try:
        shutil.rmtree(path)
        #print "rm %s" % path
    except:
        logMsg("remove_all", 'unkonow', 2)


def remove_expired_path(path, expired, file_match, clear_file, del_path):
    _match = file_match.split(",")

    # 删除过期文件
    for root, dirs, files in os.walk(path):
        if files:
            for file_one in files:
                file_path = os.path.join(root, file_one)
                if os.path.islink(file_path) or os.path.ismount(file_path):  # 过滤链接和挂载点文件
                    pass
                else:
                    if compare_file_time(file_path, expired):
                        for _match_one in _match:
                            if re.search(_match_one, file_one):
                                _remove(os.path.join(root, file_one), "file")
    if del_path:
        # 删除空目录
        for root, dirs, files in os.walk(path):
            for dir_one in dirs:
                dir_path = os.path.join(root, dir_one)
                if len(os.listdir(dir_path)) == 0:
                    _remove(dir_path, "dir")


def remove_rematch_dir(path, expired, dir_match):
    # 得到path下的目录列表
    current_dirs = list()
    current_all = os.listdir(path)
    for current_one in current_all:
        if os.path.isdir(os.path.join(path, current_one)):
            current_dirs.append(current_one)

    # 按日期时间匹配
    expired_dirs = list()
    for dir_one in current_dirs:
        if compare_file_time(os.path.join(path, dir_one), expired):
            expired_dirs.append(dir_one)

    # 匹配目录列表中符合规则的目录
    need_remove_dirs = list()
    if dir_match == "*":
        need_remove_dirs = expired_dirs
    else:
        for _match in dir_match.split(","):
            for match_one in expired_dirs:
                if re.search(_match, match_one):
                    need_remove_dirs.append(match_one)
    # pdb.set_trace()
    # 删除目录
    for _remove_dirs in need_remove_dirs:
        remove_dir = os.path.join(path, _remove_dirs)
        print "remove dirs %s" % remove_dir
        _remove_all(remove_dir)


def compare_file_time(file, day):
    import time
    time_of_last_access = os.path.getctime(file)
    age_in_day = (time.time() - time_of_last_access) / (60 * 60 * 24)
    if age_in_day > int(day):
        return True
    return False


def main():
    configName = "/data/tools/remove_expired.ini"
    data = getConfig(configName)
    for _data in data:
        path = _data.get("var_path", None)
        expired = _data.get("expired", 7)
        file_match = _data.get("file_match", None)
        clear_file = _data.get("clear_file", None)
        dir_match = _data.get("dir_match", None)
        if _data.get("del_path", None):
            del_path = _data.get("del_path", None)
        else:
            del_path = 0
        if not dir_match:
            remove_expired_path(path, expired, file_match, clear_file, del_path)
        elif dir_match:
            remove_rematch_dir(path, expired, dir_match)


if __name__ == "__main__":
    main()
