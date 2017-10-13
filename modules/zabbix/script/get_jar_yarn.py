# -*- coding: utf-8 -*-
import commands


def run_cmd(cmd):
    out = commands.getoutput(cmd)
    return out


def write_file(filename, data):
    with open(filename, 'a+') as f:
        msg = data + '\n'
        f.write(msg)
    return True


def main():
    my_dict = dict()
    base_cmd = "java -jar /usr/bin/cmdline-jmxclient-0.10.3.jar - 10.255.128.2:7777"
    project = run_cmd(base_cmd).split('\n')
    for one_project in project:
        my_list = list()
        get_item_cmd = "%s %s" % (base_cmd, one_project)
        item_list = run_cmd(get_item_cmd).split('\n')
        for item in item_list:
            my_list.append(item)
        my_dict[one_project] = my_list

    filename = 'yarn_datenode.list'
    import json
    write_file(filename, json.dumps(my_dict, indent=2))


if __name__ == "__main__":
    main()
