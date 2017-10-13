#!/usr/bin/python
#-*-coding:UTF-8 -*-
import sys

sys.argv.pop(0)

rack = {
        "10.255.129.201": "/rack1",
        "10.255.129.202": "/rack1",
        "10.255.129.203": "/rack1",
        "10.255.129.204": "/rack2",
        "10.255.129.205": "/rack2",
        "10.255.129.206": "/rack2",
        }


if __name__=="__main__":
        for ip in sys.argv:
            print rack.get(ip,"/rack-default")
