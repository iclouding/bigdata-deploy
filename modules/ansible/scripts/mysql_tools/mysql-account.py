#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import subprocess
import sys
import warnings


class MysqlBase():
    # 初始化mysql连接
    def __init__(self, ip="10.10.1.1", user="root", passwd='11', databases='zabbix'):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.databases = databases
        try:
            self.conn = MySQLdb.connect(self.ip, self.user, self.passwd, self.databases)
        except:
            raise ValueError("mysql connect failed %s") % self.ip
        self.curs = self.conn.cursor()
        self.curs.execute('SET NAMES utf8')

    def __del__(self):
        self.curs.close()
        self.conn.close()

    def insert(self, table, data):
        _field = ','.join(['`%s`' % (k_insert) for k_insert in data.keys()])
        _value = ','.join(["'%s'" % (self.conn.escape_string(str(v_insert))) for v_insert in data.values()])
        _sql = 'INSERT INTO `%s`(%s) VALUES(%s)' % (table, _field, _value)
        print _sql

        self.curs.lastrowid = 0
        try:
            self.curs.execute(_sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise ValueError("insert error %s" % _sql)

        return self.curs.lastrowid

    def update(self, table, data, condition):
        _field = ','.join(["`%s`='%s'" % (k_update, self.conn.escape_string(str(data[k_update]))) for k_update in data])
        _sql = "UPDATE `%s` SET %s where %s" % (table, _field, condition)

        resNum = 0
        try:
            resNum = self.curs.execute(_sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise ValueError("update error %s" % _sql)

        return resNum

    def delete(self, table, condition):
        _sql = 'DELETE FROM `%s` WHERE %s' % (table, condition)
        resNum = 0
        try:
            resNum = self.curs.execute(_sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise ValueError('delete error %s' % _sql)
        return resNum

    def query(self, sql):
        res = ''
        try:
            self.curs.execute(sql)
            res = self.curs.fetchall()
        except:
            raise ValueError('query error %s' % sql)
        return res

    def change(self, sql, many=False):
        ###过滤unknow table的warning
        warnings.filterwarnings('ignore')
        resNum = 0
        if many:
            try:
                resNum = self.curs.executemany(sql, many)
                self.conn.commit()
            except:
                self.conn.rollback()
                raise ValueError('exec error %s' % sql)
        else:
            try:
                resNum = self.curs.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                raise ValueError('exec error %s' % sql)

        return resNum


def initlog():
    import logging
    logger = None
    logger = logging.getLogger()
    log_name = sys.argv[0].split(".")[0] + ".log"
    hdlr = logging.FileHandler(log_name)
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


def _run_cmd(cmd):
    print "Starting run: %s " % cmd
    cmdref = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out = cmdref.stdout.read()
    print "run cmd  output " + out
    data = cmdref.communicate()
    if cmdref.returncode == 0:
        msg = "Run %s success \n" % cmd
        msg = msg + data[0]
        print(msg)
        return True
    else:
        msg = "[ERROR] Run %s False \n" % cmd
        msg = msg + data[1]
        logMsg("Run", msg, 2)
        raise "Run cmd ERROR !"


def get_account_by_host(hostname):
    # '10.10.88.176', '123.59.83.223','root', 'moresmarTV@608', 'bigdata'
    yunwei_host= '123.59.83.223'
    user = 'root'
    passwd = 'moresmarTV@608'
    db = 'bigdata'

    sql = "select `login-user`,`login-password`,`host`,`name`," \
          "`password`,priv,`remote-host`,`database` from mysql_account where host='%s'"%hostname

    # ip="10.10.1.1", user="root", passwd='11', databases='zabbix'
    m = MysqlBase(ip=yunwei_host, user=user, passwd=passwd, databases=db)
    data = m.query(sql)
    return data


def add_acclount(data):
    for line in data:
        if line:
            login_user, login_passwd, host, name, passwd, priv, remote_host, database = line
            cmd = """mysql -u{login_user} -p{login_passwd} -h{host}  -e 'grant {priv} on {database}.* to {name}@'{remote_host}'
                   IDENTIFIED BY '{passwd}';'""".format \
                (login_user=login_user, login_passwd=login_passwd,
                 host=host, priv=priv, database=database, name=name, remote_host=remote_host,passwd=passwd)
            _run_cmd(cmd)
    return True


def main():
    data = get_account_by_host()
    if data:
        add_acclount(data)
    else:
        raise "Not get account info which need add from Database"


if __name__ == '__main__':
    main()
