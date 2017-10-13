# coding:utf-8 

import pexpect
import logging
from multiprocessing.dummy import Pool

def ssh_cmd(host, user_name, pwd, cmd, retry_times=3, timeout=5):
    status = -1
    ssh = pexpect.spawn('ssh %s@%s "%s"' % (user_name, host, cmd))
    try: 
        remote_status = ssh.expect(['password:', 'continue connecting (yes/no)?'], timeout=timeout) 
        if remote_status == 0:
            pass
        elif remote_status == 1: 
            ssh.sendline('yes') 
            ssh.expect('password: ') 
        ssh.sendline(pwd) 
        ssh.sendline(cmd) 
        remote_output = ssh.read() 
        status = 0 
    except pexpect.EOF, e: 
        remote_output = "EOF:" + str(e)
        ssh.close() 
        status = -1 
    except pexpect.TIMEOUT, e: 
        remote_output =  "TIMEOUT" + str(e)
        ssh.close() 
        status = -2 
    if retry_times < 0 or status == 0:
        return status, remote_output
    else:
        return ssh_cmd(host, user_name, pwd, cmd, retry_times-1, timeout)


def ssh_cmds(host, user_name, pwd, cmds, timeoout=5):
    o_status = 0
    o_outputs = []
    for cmd in cmds:
        status, output = ssh_cmd(host, user_name, pwd, cmd, timeoout)
        logging.info('host[%s] cmd[%s] status[%d] output[%s]' % (host, cmd, status, output))
        o_outputs.append((host, cmd, output))
        if status != 0:
            logging.error('cmd failed:host[%s] cmd[%s]' % (host, cmd))
            o_status = -1
            break 
    return o_status, o_outputs


def distributed_ssh_cmds(host_list, user_name, pwd, cmds):
    pool = Pool()
    results = []
    for host in host_list:
        #ssh_cmds(host, user_name, pwd, cmds)
        x = pool.apply_async(ssh_cmds, (host, user_name, pwd, cmds))
        results.append(x.get())
    pool.close()
    pool.join()
    return results

    
