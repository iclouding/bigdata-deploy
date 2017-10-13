#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import json


def write_file(filename, data):
    data = data.strip() + '\n'
    with open(filename, 'a+') as f:
        f.write(data)
    return True


def run(output):
    data = sys.stdin.readline()
    try:
        data_n = json.loads(data)
    except:
        print "Input not json format "
    write_file(output, data)
    print(json.dumps(data_n, indent=1))


def main():
    output = 'output.log'
    while 1:
        run(output)


if __name__ == "__main__":
    main()
