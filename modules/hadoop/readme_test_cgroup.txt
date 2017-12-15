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

6.重启node manager
ansible all -i test_cgroup_nodes.host -mshell -a"su - yarn -c  ' cd /opt/hadoop/sbin; ./yarn-daemons.sh stop nodemanager'"
ansible all -i test_cgroup_nodes.host -mshell -a"su - yarn -c  ' cd /opt/hadoop/sbin; ./yarn-daemons.sh start nodemanager'"

7.重启resourcemanager
ansible all -i test_cgroup_nodes.host -mshell -a"su - yarn -c  ' cd /opt/hadoop/sbin; ./yarn-daemons.sh stop resourcemanager'"
ansible all -i test_cgroup_nodes.host -mshell -a"su - yarn -c  ' cd /opt/hadoop/sbin; ./yarn-daemons.sh start resourcemanager'"


note:
hadoop 用户改动fair-scheduler.xml
yarn用户重启resourceManager