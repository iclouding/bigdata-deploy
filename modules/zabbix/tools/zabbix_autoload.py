#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
# 从table读入hostip和服务信息，自动加载zabbix对应模块
import sys
import MySQLdb
import pdb
import json
from pyzabbix import ZabbixAPI


def logMsg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    import logging
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


class Myzabbix():
    def __init__(self, url, user, passwd):
        self.url = url
        self.user = user
        self.passwd = passwd
        try:
            self.zapi = ZabbixAPI(self.url)
            self.zapi.login(self.user, self.passwd)
        except:
            msg = "Login zabbix Url %s failed,please check it!" % self.url
            logMsg("zabbix_login", msg, 2)
            raise "Login zabbix failed"

    def get_templateid(self, template_name):
        try:
            res = self.zapi.template.get(filter={'host': template_name})
            # res 返回结果[{u'hostid': u'11661', u'templateid': u'11661'}]
            if res:
                # res 返回结果[{u'hostid': u'11661', u'templateid': u'11661'}]
                templateid = res[0]['templateid']
                return int(templateid)
            else:
                msg = "%s not find in zabbix" % template_name
                logMsg("get_templateid", msg, 2)
                return False
        except:
            error_msg = "get template_name %s" % template_name
            raise (error_msg)

    def get_hostid(self, hostname):
        '''获取host对应的hostid'''
        # host='bigdata-computing-01-001'
        ##pdb.set_trace()
        # res 返回'''[{u'hostid': u'12804'}]'''
        try:
            res = self.zapi.host.get(filter={'host': hostname})
            hostid = res[0]['hostid']
        except:
            msg = "get hostid error ,maybe hostname %s not in zabbix" % hostname
            logMsg("get_hostid", msg, 2)
            raise KeyError, "could not find hostname"
        return hostid


    def get_templateid_list(self, hostid):
        # 获取host原有的模版templateid
        res_templated = self.zapi.template.get(output="hostid", selectParentTemplates="refer", hostids=hostid)
        # template_old = [int(m['templateid']) for m in res]
        templateid_list = [{'templateid': int(m['templateid'])} for m in res_templated]
        return templateid_list

    def updated_template(self, hostname, template_list):
        self.hostid = self.get_hostid(hostname)
        templateid_list = list()
        msg_template = "%s need add %s" % (hostname, json.dumps(template_list, indent=1))
        logMsg("get_template", msg_template, 1)

        for template_name in template_list:
            template_id = self.get_templateid(template_name)
            templateid_list.append(template_id)

        # get old template by hostname
        templateid_list_old = self.get_templateid_list(self.hostid)

        # get templateid list which need updated

        templateid_list_updated = list()
        for item in templateid_list:
            if item in templateid_list_old:
                continue
            else:
                templateid_list_updated.append({'templateid': item})
        # 绑定模板到对应服务器
        res = self.zapi.host.update(hostid=self.hostid, templates=templateid_list_updated)
        msg = "mount %s %s" % (hostname, json.dumps(templateid_list_updated, indent=1))
        logMsg("add_rule", msg, 1)


def create_template_by_hostip(ip):
    db = MySQLdb.connect('10.10.88.176', 'root', 'moresmarTV@608', 'bigdata')
    cursor = db.cursor()
    publish_sql = "select DISTINCT service from bigdata_service where up_addr_p='%s' and states=1 ;" % ip
    cursor.execute(publish_sql)
    data = cursor.fetchall()
    data_list = []
    if data:
        for _data in data:
            _data = 'bigdata-monitor-' + _data[0].strip()
            data_list.append(_data)
    data_list.append("bigdata-monitor-base")
    return data_list


def get_bigdata_hostip():
    db = MySQLdb.connect('10.10.88.176', 'root', 'moresmarTV@608', 'bigdata')
    cursor = db.cursor()
    publish_sql = "select hostname, up_addr_p from bigdata_host where states=1;"
    cursor.execute(publish_sql)
    data = cursor.fetchall()
    return data


if __name__ == "__main__":
    bigdata_host_list = get_bigdata_hostip()
    url = "http://10.10.154.153/zabbix"
    user = "pengtao"
    passwd = "tel7206324"
    zabbix_ = Myzabbix(url, user, passwd)
    # pdb.set_trace()
    for line in bigdata_host_list:
        hostname, hostip = line
        template_list = create_template_by_hostip(hostip)
        zabbix_.updated_template(hostname, template_list)
