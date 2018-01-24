1.安装cgroup
cd /data/tools/ansible/modules/hadoop/playbook
ansible all -i test_cgroup.host -mshell -a"yum install -y libcgroup-tools"

2.启动cgroup
ansible all -i test_cgroup.host -mshell -a"systemctl start cgconfig.service"

3.查看cgroup服务是否启动成功
ansible all -i test_cgroup.host -mshell -a"systemctl status cgconfig.service"

4.创建hadoop-yarn命名的cgroup
ansible all -i test_cgroup.host -mshell -a"cd /sys/fs/cgroup/cpu;mkdir -p hadoop-yarn"

5.分发yarn配置[包含app]
ansible-playbook -i test.host install_hadoop-bin_test_group.yml -t config
ansible all -i test_cgroup.host -mshell -a"cd /sys/fs/cgroup/cpu;mkdir -p hadoop-yarn"
ansible all -i test_cgroup.host -mshell -a"cd /sys/fs/cgroup/cpu,cpuacct;chmod 777 -R hadoop-yarn"
ansible all -i test_cgroup.host -mshell -a"cd /opt;chown root:hadoop hadoop"
ansible all -i test_cgroup.host -mshell -a"cd /opt/hadoop;chown root:hadoop etc"
ansible all -i test_cgroup.host -mshell -a"cd /opt/hadoop/etc;chown root:hadoop hadoop"
ansible all -i test_cgroup.host -mshell -a"cd /opt/hadoop/bin;chown root:hadoop container-executor"
ansible all -i test_cgroup.host -mshell -a"cd /opt/hadoop;chmod 6050 bin/container-executor"
ansible all -i test_cgroup.host -mshell -a"cd /sys/fs/cgroup/;chmod 777 'cpu,cpuacct'"


6.重启resourcemanager [yarn用户]
sh /opt/hadoop/sbin/yarn-daemon.sh stop resourcemanager
sh /opt/hadoop/sbin/yarn-daemon.sh start resourcemanager


7.重启node manager [yarn用户]
重启所有node manager[需要在RM上执行]
sh /opt/hadoop/sbin/yarn-daemons.sh stop   nodemanager
sh /opt/hadoop/sbin/yarn-daemons.sh start  nodemanager
yarn rmadmin -refreshNodes
单台重启node manager
sh /opt/hadoop/sbin/yarn-daemon.sh stop  nodemanager
sh /opt/hadoop/sbin/yarn-daemon.sh start nodemanager


note:
bigtest-cmpt-129-202 机器 创建a目录，不能删除/sys/fs/cgroup/cpu/hadoop-yarn/a
hadoop用户改动fair-scheduler.xml、yarn-site.xml文件
yarn用户重启resourceManager