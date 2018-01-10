#!/usr/bin/python
#-*-coding:UTF-8 -*-
import sys

sys.argv.pop(0)

rack = {
        "10.255.129.104": "/rack1",
        "10.255.129.105": "/rack1",
        "10.255.129.106": "/rack1",
        "10.255.129.107": "/rack2",
        "10.255.129.108": "/rack2",
        "10.255.129.109": "/rack2",
        }


if __name__=="__main__":
        for ip in sys.argv:
            print rack.get(ip,"/rack-default")
