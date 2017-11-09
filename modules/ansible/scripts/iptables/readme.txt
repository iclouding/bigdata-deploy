-- 更新web_bi防火墙规则
ansible-playbook -i ucloud_web_bi.host sync_iptables_extsrv_web_bi.yml

-- 更新collect01防火墙规则
ansible-playbook -i ucloud_collect01.host sync_iptables_extsrv_collect01.yml

-- 更新collect02防火墙规则
ansible-playbook -i ucloud_collect02.host sync_iptables_extsrv_collect02.yml
