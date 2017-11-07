#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sdk import UcloudApiClient
from config import *
import sys
import json
import pdb
import time


# 实例化 API 句柄


class MyUcloud():
    def __init__(self):
        self.ApiClient = UcloudApiClient(base_url, public_key, private_key)

    def get_eip_info(self):
        data = list()
        for i in range(0, 10):
            Parameters = {"Action": "DescribeEIP", "Region": "cn-bj2", "Limit": 100, "Offset": i}
            # data = list()
            response = self.ApiClient.get("/", Parameters)
            if response:
                for one_item in response['EIPSet']:
                    if one_item['Resource']['ResourceType'] != 'uhost':
                        temp = (one_item['Bandwidth'], one_item['EIPAddr'][0]['IP'], one_item['EIPId'],
                                one_item['Resource']['ResourceName'], one_item['Weight'],
                                one_item['Resource']['ResourceType'])
                        data.append(temp)
                        del temp
                        # <type 'tuple'>: (2, u'123.59.42.216', u'eip-0v0by0', u'Platform-middleware-URDTServer03', 50)
        # print json.dumps(data, indent=1)
        return data

    def get_eip_bandwidth(self, eipid_list):
        return_data = dict()
        Parameters = {"Action": "DescribeBandwidthUsage", "Region": "cn-bj2"}
        response = self.ApiClient.get("/", Parameters)
        alL_data = response['EIPSet']
        for one_data in alL_data:
            eipid = one_data["EIPId"]
            bandwidth = one_data['CurBandwidth']
            if eipid in eipid_list:
                return_data[eipid] = bandwidth
        return return_data

    def get_single_bandwidth(self, eipid):
        Parameters = {"Action": "DescribeBandwidthUsage", "Region": "cn-bj2", "EIPIds.1": eipid}
        response = self.ApiClient.get("/", Parameters)
        alL_data = response['EIPSet']
        return alL_data[0]['CurBandwidth']


def write_file(filename, data):
    with open(filename, 'a+') as f:
        f.write(data)


def main():
    # check_ip = ("106.75.73.131", "106.75.9.12")]
    eipid_dict = dict()

    ip_list = ["106.75.73.131", "106.75.9.12", "106.75.50.197", "106.75.2.45", "106.75.62.85", "106.75.14.143",
               "106.75.86.137", "106.75.6.190", "106.75.87.236", "106.75.9.59", "106.75.87.144", "106.75.12.215",
               "106.75.100.16", "106.75.49.238", "106.75.101.78", "106.75.15.116"]
    eip_id = ["eip-3sfsym", "eip-vwulua", "eip-flahuh", "eip-u5fbsa", "eip-4jfaey", "eip-rn2fk5", "eip-4ifnai",
              "eip-nbj533", "eip-agrzl2", "eip-itrraf", "eip-kqnbon", "eip-eqyymm", "eip-jbra5u", "eip-2emgq1",
              "eip-soezen", "eip-2au02k"]

    u = MyUcloud()
    filename = 'get_eip.log'
    while 1:

        for i in range(len(eip_id)):
             eipid_dict[ip_list[i]] = u.get_single_bandwidth(eip_id[i])

    # filename  print "get data"
    # print json.dumps(eipid_dict, indent=1)

        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        data = "{0}\n{1}\n".format(now, json.dumps(eipid_dict, indent=1))
        write_file(filename, data)
        time.sleep(60)




    # eip_info = u.get_eip_info()
    # eipid_list = list()
    # for info in eip_info:
    #     eipid_list.append(info[2])
    # eip_bandwith = u.get_eip_bandwidth(eipid_list)
    #
    # for item in eip_bandwith.keys():
    #     for a in eip_info:
    #         if item == a[2]:
    #             print "{0}  :   {1}".format(a[1], eip_bandwith[item])
    #
    #             # print json.dumps(eip_bandwith,indent=1)
    #
    #             # http://api.ucloud.cn/?Action=DescribeBandwidthUsage&Region=cn-bj2&EIPIds.1=eip-vwulua


if __name__ == '__main__':
    main()
