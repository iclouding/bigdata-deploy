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

    def create_firewall(self, fire_name, rules):
        """
        http(s)://api.ucloud.cn/?Action=CreateSecurityGroup
    &Region=cn-bj2
    &GroupName=NewSecurityGroup
    &Rule.1=UDP|53|0.0.0.0/0|ACCEPT|50
    &Rule.0=TCP|3306|0.0.0.0/0|DROP|50
        :param rule: rule
        :return: True/False
        """
        Parameters = {"Action": "CreateSecurityGroup", "GroupName": fire_name, "Region": "cn-bj2",
                      "Description": fire_name}
        for i in range(len(rules)):
            key = "Rule.%s" % str(i)
            Parameters[key] = rules[i]

        # data = list()
        response = self.ApiClient.get("/", Parameters)

        return response


def write_file(filename, data):
    with open(filename, 'a+') as f:
        f.write(data)


def read_file(filename):
    with open(filename, "r") as f:
        data = f.read()
    return data


def main():

    filrewall_name = sys.argv[1]
    rule_name=filrewall_name[5:]
    if len(sys.argv) != 2:
        raise KeyError

    data=read_file(filrewall_name).split('\n')
    rule=list()
    for line in data:
        if line:
            rule.append(line.strip())

    u=MyUcloud()
    u.create_firewall(rule_name,rule)


if __name__ == '__main__':
    main()
