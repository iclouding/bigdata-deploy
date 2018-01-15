利用linux cgroup控制计算节点cpu

----------------------------------------生产环境----------------------------------------
--cgroup安装包分发
ansible-playbook -i product.host cgroup_product.yml -t cgroup_install

--配置分发&并设定机器重启后自动拉起服务
ansible-playbook -i product.host cgroup_product.yml -t cgroup_config

--重启cgconfig和cgred服务
ansible-playbook -i product.host cgroup_product.yml -t cgroup_restart

--启动cgconfig和cgred服务
ansible-playbook -i product.host cgroup_product.yml -t cgroup_start

--停止cgconfig和cgred服务
ansible-playbook -i product.host cgroup_product.yml -t cgroup_stop

--查看cgconfig状态
ansible nodemanager -i product.host -mshell -a"systemctl status cgconfig.service"

--查看cgred状态
ansible nodemanager -i product.host -mshell -a"systemctl status cgred.service"

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

--查看cgconfig状态
ansible nodemanager -i test.host -mshell -a"systemctl status cgconfig.service"

--查看cgred状态
ansible nodemanager -i test.host -mshell -a"systemctl status cgred.service"

----------------------------------------命令集合----------------------------------------
删除无用的cgroup组
ansible nodemanager -i test.host -mshell -a"cgdelete -g cpu:limitcpu"
ansible nodemanager -i test.host -mshell -a"cgdelete -g memory:limitcpu"
ansible nodemanager -i host.host -mshell -a"systemctl restart cgred "
ansible nodemanager -i host.host -mshell -a"systemctl restart cgconfig "
systemctl restart cgconfig
systemctl restart cgred
systemctl status cgconfig
systemctl status cgred

