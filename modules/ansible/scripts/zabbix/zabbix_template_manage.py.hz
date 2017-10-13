#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
# propose:  批量刷新host管理的模版
import os
import copy
import MySQLdb
import pdb
from pyzabbix import ZabbixAPI


def zabbix_login():
    zabbix_server ="http://10.10.154.153/zabbix" # "http://monitor.whaley.cn/zabbix/"
    zabbix_user = "pengtao"
    zabbix_passwd = "tel7206324"

    zapi = ZabbixAPI(zabbix_server)
    zapi.login(zabbix_user, zabbix_passwd)
    return zapi


def get_templateid(zapi, template_name):
    '''获取需要添加的模版的templateid'''
    res = zapi.template.get(filter={'host': template_name})
    # res 返回结果[{u'hostid': u'11661', u'templateid': u'11661'}]
    if res:
    # res 返回结果[{u'hostid': u'11661', u'templateid': u'11661'}]
        templateid = res[0]['templateid']
        templateid = int(templateid)
        return templateid
    else:
        return False


def check_template(zapi, hostname, template_list):
    '''获取host对应的hostid'''
    # host='bigdata-computing-01-001'
    res = zapi.host.get(filter={'host': hostname})
    ##pdb.set_trace()
    # res 返回'''[{u'hostid': u'12804'}]'''
    try:
        hostid = res[0]['hostid']
    except:
        pass

    '''获取host原有的模版templateid'''
    res = zapi.template.get(output="hostid", selectParentTemplates="refer", hostids=hostid)
    template_old = [int(m['templateid']) for m in res]
    template_old_format = [{'templateid': int(m['templateid'])} for m in res]
    print '-' * 100
    print template_old_format

    # change template name to templateid like bigdata-service-riak to num
    new_template_list=[]
    for template_name in template_list:
        template_id_new=get_templateid(zapi=zapi,template_name=template_name)
        if template_id_new:
            new_template_list.append(template_id_new)


    template_new = copy.deepcopy(template_old_format) ##??
    for templateid in new_template_list:
        if templateid in template_old:
            continue
        else:
            template_new.append({'templateid': templateid})
    res = zapi.host.update(hostid=hostid, templates=template_new)
    # print res[0]


def get_hostname_template_db(local_ip):
    db = MySQLdb.connect('10.10.88.176', 'root', 'moresmarTV@608', 'bigdata')
    # cursor = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cursor = db.cursor()
    publish_sql = "select DISTINCT service from service_host where up_addr_p='%s';" % local_ip

    cursor.execute(publish_sql)
    data = cursor.fetchall()
    data_list = []
    if data:
        for _data in data:
            _data = 'bigdata-service-' + _data[0].strip()
            data_list.append(_data)
    # hostname_sql = "select hostname from host_info where up_addr_p='%s'" % local_ip
    # cursor.execute(hostname_sql)
    # hostname=cursor.fetchone()

    return data_list


def get_local_ip():
    import socket
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    return myname, myaddr

def get_host_info():
    db = MySQLdb.connect('10.10.88.176', 'root', 'moresmarTV@608', 'bigdata')
    cursor = db.cursor()
    publish_sql = "select hostname, up_addr_p from host_info ;"
    cursor.execute(publish_sql)
    data = cursor.fetchall()
    return data 

if __name__ == "__main__":
    zapi = zabbix_login()
    get_data = get_host_info()
    ##pdb.set_trace()
    for data_oneline in get_data:
       hostname,hostip = data_oneline
       template_list = get_hostname_template_db(hostip)
       print "Link hostname :",hostname
       check_template(zapi,hostname,template_list)
