#!/usr/bin/python
#-*-coding:UTF-8 -*-
import sys

sys.argv.pop(0)

rack = {
        "10.255.129.110": "/rack1",
        "10.255.129.111": "/rack1",
        "10.255.129.112": "/rack1",
        "10.255.129.113": "/rack1",
        }


if __name__=="__main__":
        for ip in sys.argv:
            print rack.get(ip,"/rack-default")
