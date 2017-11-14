# -*- coding: utf-8 -*-
import commands
import logging
import sys


def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = logging.getLogger()
    logname = sys.argv[0] + '.logs'
    hdlr = logging.FileHandler(logname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)


def run_cmd_out(cmd):
    status, output = commands.getstatusoutput(cmd)
    if status == 0:
        return output
    else:
        msg = "run {0} Failed,output was {1}".format(cmd, output)
        log_msg("run", msg, 2)
        raise Exception(msg, 2)


def get_size(paths):
    hdfs_size = dict()
    for one_item in paths:
        get_size_cmd = "hadoop fs -du -s  %s" % one_item
        out_size = run_cmd_out(get_size_cmd)
        try:
            hdfs_size[one_item] = int(out_size.split()[0])
            data="{0},{1}\n".format(one_item,out_size.split()[0])
            with open("3.list", 'a+') as f:
                f.write(data)
        except:
            msg_err = "get %s size failed" % one_item
            log_msg("get_size", msg_err, 2)
    return hdfs_size


def get_all_dirname(pathname):
    cmd = "hadoop fs -ls %s" % pathname
    output = run_cmd_out(cmd)
    paths = list()
    for line in output.split('\n'):
        if line[0] == 'd':
            path = line.split()[-1]
            paths.append(path)
    return paths


def main():
    pathname = sys.argv[1]
    paths = get_all_dirname(pathname)


    hdfs_size = get_size(paths)

    import json
    print json.dumps(hdfs_size, indent=1)

    with open ("1.log",'a+') as f:
        f.write(json.dumps(hdfs_size, indent=1))


if __name__ == "__main__":
    main()
