# -*- coding: utf-8 -*-
import commands
import time


def run_cmd(cmd):
    out = commands.getoutput(cmd)
    return out


def write_file(filename, data):
    with open(filename, 'a+') as f:
        msg = data + '\n'
        f.write(msg)
    return True


def main():
    filename = '/tmp/mysql_processlist.log'
    base_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    msg = "Time :%s\n" % base_time
    write_file(filename, msg)

    base_cmd = "mysqladmin -uroot -pmoretvsmarTV@608_810 --verbose processlist"
    data = run_cmd(base_cmd)
    write_file(filename, data)
    write_file(filename, '\n')


if __name__ == "__main__":
    main()

