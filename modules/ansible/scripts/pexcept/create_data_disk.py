# coding:utf-8
import sys
import logging
import ConfigParser
import os
import subprocess
import pexpect
import pdb


def initlog():
    logger = logging.getLogger()
    log_name = sys.argv[0].split(".")[0] + ".log"
    hdlr = logging.FileHandler(log_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return [logger, hdlr]


def logMsg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger, hdlr = initlog()
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)  # 网络上的实现基本为说明这条语句的使用和作用


def get_config(filename, values):
    cf = ConfigParser.SafeConfigParser()
    cf.read(filename)
    config_data_section = cf.sections()
    return_data = {}

    if values in config_data_section:
        _list = cf.items(values)
        for _key, _value in _list:
            return_data[_key] = _value
    else:
        print "[ERROR] %s is not in config files,PLS check it %s" % (values, filename)
        msg_info = "===%s: Get info Failed!!===" % values
        logMsg("get_config", msg_info, 2)
        raise "Values could`t found in config"
    return return_data


def create_disk(device, disk):
    if not check_disk(device, disk):
        parted_disk(device)
        mkfs_disk(device)
        mount_disk(device, disk)
        return True
    else:
        msg = "Disk %s is created !" % disk
        logMsg('create_disk', msg, 2)
        return False


def parted_disk(device):
    cmd_parted = "parted %s" % device
    p = pexpect.spawn(cmd_parted)
    p.expect("(parted)")
    p.sendline('mklabel gpt')
    p.expect("是/Yes/否/No?")
    p.sendline('yes')
    p.expect("(parted)")
    p.sendline('mkpart primary 0 -1')
    p.expect("忽略/Ignore/放弃/Cancel?")
    p.sendline('Ignore')
    p.expect("(parted)")
    p.sendline('quit')


def mkfs_disk(device):
    cmd = "mkfs.xfs -f %s" % device
    _run_cmd(cmd)


def mount_disk(device, disk):
    # mount disk
    device_lable = "%s1" % device
    cmd = "mkdir -p %s && mount %s %s" % (disk, device_lable, disk)
    _run_cmd(cmd)
    # add disk to /etc/fstab
    # get uuid from " blkid /dev/sdb1"
    cmd_blkid = 'blkid %s' % device_lable
    uuid = _run_cmd(cmd_blkid, True).split('=')[1][1:-5]
    txt_values = 'UUID=%s %s xfs defaults 1 2' % (uuid, disk)
    cmd_add_fatab = 'echo "%s" >> /etc/fstab' % txt_values
    _run_cmd(cmd_add_fatab)


def check_disk(device, disk):
    #     df -lTH|grep /miles output /dev/sdb1               xfs        22G   34M   22G    1% /miles
    check_cmd = "df -h|grep %s$" % disk
    out = _run_cmd(check_cmd, True)
    if device in out and disk in out:
        return True
    else:
        return False


def _run_cmd(cmd, is_value=False):
    pdb.set_trace()
    print "Starting run: %s " % cmd
    cmdref = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out = cmdref.stdout.read()
    print "run cmd  output " + out
    data = cmdref.communicate()
    if cmdref.returncode == 0:
        msg_success = "Run %s success \n" % cmd
        msg_success += data[0]
        print(msg_success)
        if is_value:
            return out
        return True
    else:
        msg_failed = "[ERROR] Run %s False \n" % cmd
        msg_failed += data[1]
        logMsg("Run", msg_failed, 2)
        raise "Run cmd ERROR !"


def main():
    config_file = os.path.join(os.path.abspath('.'), 'create_data_disk.ini')
    cf = ConfigParser.SafeConfigParser()
    cf.read(config_file)
    disk_pool = cf.sections()

    for crate_disk in disk_pool:
        config_ = get_config(config_file, crate_disk)
        device = config_.get('device', None)
        disk = config_.get('disk', None)
        create_disk(device, disk)
        if check_disk(device, disk):
            msg = 'create disk %s Success' % disk
            logMsg('check_disk', msg, 1)


if __name__ == "__main__":
    main()
