利用linux cgroup控制计算节点cpu







----------------------------------------测试环境----------------------------------------
--cgroup安装包分发
ansible-playbook -i test.host cgroup_test.yml -t cgroup_install

--配置分发&并设定机器重启后自动拉起服务
ansible-playbook -i test.host cgroup_test.yml -t cgroup_config

--重启cgconfig和cgred服务
ansible-playbook -i test.host cgroup_test.yml -t cgroup_restart

--启动cgconfig和cgred服务
ansible-playbook -i test.host cgroup_test.yml -t cgroup_start

--停止cgconfig和cgred服务
ansible-playbook -i test.host cgroup_test.yml -t cgroup_stop
----------------------------------------测试环境----------------------------------------

