# -*- coding: utf-8 -*-
# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# this is the Interface package of Ansible2 API
#

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from tempfile import NamedTemporaryFile
import os


class AnsibleTask(object):
    def __init__(self, targetHost):
        Options = namedtuple(
            'Options', [
                'listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path',
                'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user',
                'verbosity', 'check'
            ]
        )

        # initialize needed objects
        self.variable_manager = VariableManager()

        self.options = Options(
            listtags=False, listtasks=False, listhosts=False, syntax=False, connection='smart',
            module_path='/usr/lib/python2.7/site-packages/ansible/modules', forks=100,
            remote_user='root', private_key_file=None, ssh_common_args=None, ssh_extra_args=None,
            sftp_extra_args=None, scp_extra_args=None, become=False, become_method=None, become_user='root',
            verbosity=None, check=False
        )
        self.passwords = dict(vault_pass='secret')
        self.loader = DataLoader()

        # create inventory and pass to var manager
        self.hostsFile = NamedTemporaryFile(delete=False)
        self.hostsFile.write(targetHost)
        self.hostsFile.close()
        self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager,
                                   host_list=self.hostsFile.name)
        self.variable_manager.set_inventory(self.inventory)

    def ansiblePlay(self, action):
        # create play with tasks
        args = "ls /"
        play_source = dict(
            name="Ansible Play",
            hosts='all',
            gather_facts='no',
            tasks=[
                dict(action=dict(module='shell', args=args), register='shell_out'),
                dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
            ]
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        # run it
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
                stdout_callback='default',
            )
            result = tqm.run(play)
        finally:
            # print result
            if tqm is not None:
                tqm.cleanup()
                os.remove(self.hostsFile.name)
                self.inventory.clear_pattern_cache()
            return result
