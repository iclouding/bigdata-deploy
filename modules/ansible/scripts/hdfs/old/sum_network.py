#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import time


def run_cmd(cmd):
    msg = "Starting run: %s " % cmd
    cmdref = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error_info = cmdref.communicate()
    return output


def main():
    network_ = list()
    num = 0
    cmd = "cat /proc/net/dev |grep em3"
    while 1:
        time.sleep(1)
        output = run_cmd(cmd)
        num_next = int(output.split()[1])
        network_.append(round((num_next - num) / 1000000, 2))
        num=num_next
        print network_[-1]

if __name__ == "__main__":
    main()
