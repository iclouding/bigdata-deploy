# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import datetime
import hashlib
import sys
from optparse import OptionParser
import subprocess
import logging


def get_opt():
    usage = '''
    This script use for get cdn values from gaoshen
    such as get_gaoshen_cdn.py -v mediags.moguv.com -d 20170405 -o /data/backups/cdn_logs/
    write to files mediags.moguv.com_20170501.gz
    -v [mediags.moguv.com/mediags.moretv.com.cn]
    '''
    parser = OptionParser(usage)
    parser.add_option("-v", "--vhost", type="string", default=False, dest="vhost",
                      help="vhost name")
    parser.add_option("-d", "--day", type="string",
                      default=(datetime.date.today() - datetime.timedelta(1)).strftime("%Y%m%d"), dest="day",
                      help="day")
    parser.add_option("-o", "--output", type="string", default='/data/backups/cdn_logs/', dest="output",
                      help="log files path")

    (options, args) = parser.parse_args()
    return options.vhost, options.day, options.output


def get_cdn_url(vhost, day, output):
    dw = {}
    now_date = datetime.datetime.now().strftime("%Y%m%d")
    if vhost == "mediags.moguv.com":
        dw['user_id'] = u'253'.replace('\'', '')
    else:
        dw['user_id'] = u'185'.replace('\'', '')

    dw['vhost'] = vhost
    dw['day'] = day
    # dw['day'] = u'20170405'.replace('\'', '')  # %Y%m%d
    dw['dtype'] = u'vod'.replace('\'', '')
    dw['logtype'] = u'access'.replace('\'', '')

    key = 'gaosheng_' + now_date

    sortdict = sorted(dw.iteritems(), key=lambda d: d[0])
    md5str = ''
    for v in sortdict:
        md5str += str(v[1])
    md5str = md5str + key
    #print 'before:', md5str
    md5 = hashlib.md5(md5str.encode('utf-8')).hexdigest()
    #print 'after:', md5
    get_url = "http://portal.gosun.com/api/downloads_log?user_id=%s&vhost=%s&day=%s&logtype=%s&dtype=%s&sign=%s" % (
        dw['user_id'], dw['vhost'], dw['day'], dw['logtype'], dw['dtype'], md5)
    #print get_url
    files = "%s_%s.gz" % (vhost, day)
    cmd = "wget  -c '%s' -O %s/%s" % (get_url, output, files)
    return cmd


def run_cmd(cmd):
    msg = "Starting run: %s " % cmd
    logMsg("run_cmd", msg, 1)
    cmdref = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error_info = cmdref.communicate()
    if not output:
        if isinstance(error_info, list) or isinstance(error_info, tuple):
            error_info = error_info[0]
        msg = "RUN %s ERROR,error" % cmd
        logMsg("run_cmd", msg, 2)
        return 1, error_info
    else:
        msg = "run %s success" % cmd
        logMsg("cmd", msg, 1)
        # print "Run Success!!"
        return 0, cmd


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


def main():
    vhost, day, output = get_opt()
    cmd = get_cdn_url(vhost, day, output)
    status, info = run_cmd(cmd)
    if status == 0:
        logMsg("run", "get cdn success", 1)
    else:
        msg = "run cmd failed,%s" % info
        logMsg("run", msg, 2)


if __name__ == "__main__":
    main()
