# -*- coding: utf-8 -*-

from common import run_cmd, write_file, get_section_values
from optparse import OptionParser
import pdb
import os
import time
import redis
import ConfigParser

base_dir = "/etc/zabbix/script/redis"


# def get_args():
#     # pdb.set_trace()
#     parser = OptionParser()
#     parser.add_option("-s", "--server", action='store', type="string", default=False, dest="hostip",
#                       help="redis hostip")
#     parser.add_option("-p", "--port", action='store', type="string", default=False, dest="port", help="Redis Port")
#     parser.add_option("-d", "--db", action='store', type="string", default=False, dest="db", help="database")
#
#     (options, args) = parser.parse_args()
#     if not options.hostip:
#         parser.error("Must input redis hostip")
#     return options


def change_dict(data):
    item_d = dict()
    for line in data.split('\n'):
        v = line.split(':')
        if len(v) == 2:
            item_d[v[0]] = v[1]
    return item_d


def get_redis_info(host, port):
    # pdb.set_trace()
    cmd = "redis-cli -h %s -p %s info" % (host, port)
    k, v = run_cmd(cmd)
    if k:
        return change_dict(v)
    else:
        print "get info form redis error host %s ,prot %s" % (host, port)


def write_info_disk(data_d, dest_dir):
    for key in data_d.keys():
        filename = os.path.join(dest_dir, key)
        write_file(filename, str(data_d[key]).strip())


def create_current_dir(dest_dir):
    # create dictory
    mkdir_cmd = "mkdir -p %s" % dest_dir
    is_ok, outout = run_cmd(mkdir_cmd)
    if not is_ok:
        raise IOError


def return_redis_keys(hostip, port, db, keys):
    r = redis.Redis(host=hostip, port=port, db=db)
    values = r.get(keys)
    return values


def redis_connect_high(hostip, port, dest_dir):
    filename = "%s/client.list.%s" % (dest_dir, time.strftime("%Y%m%d%H%M%S", time.localtime()))
    cmd = "redis-cli -h %s -p %s client list > %s" % (hostip, port, filename)
    run_cmd(cmd)


def diff_time(user_time, check_time=time.time()):
    if len(user_time) > 19:
        user_time = user_time[:19]
        user_time_mktime = time.mktime(time.strptime(user_time, '%Y-%m-%d %H:%M:%S'))
    return (int(check_time) - int(user_time_mktime))


def create_values(hostip, port, section, time_key, db):
    dest_dir = "%s/%s" % (base_dir, section)
    create_current_dir(dest_dir)
    check_key = time_key
    out_dict = get_redis_info(hostip, port)
    write_info_disk(out_dict, dest_dir)

    lasttime = return_redis_keys(hostip, port, db, check_key)
    timeout_files = os.path.join(dest_dir, 'sync_timeout')
    if not lasttime or diff_time(lasttime) > 600:
        write_file(timeout_files, lasttime or '1')
    else:
        if os.path.isfile(timeout_files):
            os.remove(timeout_files)

    if int(out_dict['connected_clients']) > 1000:
        redis_connect_high(hostip, port, dest_dir)


def main():
    config_name = os.path.join(os.path.abspath('.'), 'redis_list.conf')
    cf = ConfigParser.SafeConfigParser()
    cf.read(config_name)
    configDataSection = cf.sections()
    for section in configDataSection:
        config_data = get_section_values(section, config_name)
        hostip = config_data['hostip']
        port = config_data['port']
        time_key = config_data['time_key']
        db = config_data.get('db', 0)
        create_values(hostip, port, section, time_key, db)

    print "Data write to disk"


if __name__ == "__main__":
    main()
