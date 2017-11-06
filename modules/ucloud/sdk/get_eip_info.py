#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sdk import UcloudApiClient
from config import *
import sys
import json
import pdb
#实例化 API 句柄


class MyUcloud():
    def __init__(self):
        self.ApiClient = UcloudApiClient(base_url, public_key, private_key)

    def get_eip_info(self):
        Parameters = {"Action": "DescribeEIP", "Region": "cn-bj2"}
        data = list()
        response = ApiClient.get("/", Parameters)
        for one_item in response['EIPSet']:
            temp = (one_item['Bandwidth'], one_item['EIPAddr'][0]['IP'], one_item['EIPId'],
                    one_item['Resource']['ResourceName'], one_item['Weight'])
            data.append(temp)
            del temp
            # <type 'tuple'>: (2, u'123.59.42.216', u'eip-0v0by0', u'Platform-middleware-URDTServer03', 50)
        print json.dumps(data, indent=1)
        return data

    def get_eip_bandwidth(self,eipid):
        Parameters = {"Action": "DescribeEIP", "Region": "cn-bj2","EIPIds.n":eipid}







if __name__=='__main__':

    ApiClient = UcloudApiClient(base_url, public_key, private_key)
    #Parameters={"Action":"DescribeEIP", "Region":"cn-bj2","EIPIds.n":"eip-3sfsym"}
    Parameters = {"Action": "DescribeEIP", "Region": "cn-bj2"}
    #pdb.set_trace()
    data=list()
    response = ApiClient.get("/", Parameters )
    for one_item in response['EIPSet']:
        temp=(one_item['Bandwidth'],one_item['EIPAddr'][0]['IP'],one_item['EIPId'],one_item['Resource']['ResourceName'],one_item['Weight'])
        data.append(temp)
        del temp
        #<type 'tuple'>: (2, u'123.59.42.216', u'eip-0v0by0', u'Platform-middleware-URDTServer03', 50)
    print json.dumps(data,indent=1)





    print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
