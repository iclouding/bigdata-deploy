研发环境滚动升级hadoop2.6.3到hadoop2.9.0，并启cgroup机制。
用来测试升级过程中不影响线上服务以及cgroup的可用性。

测试点：
测试hdfs在升级过程一直可用。【编写持续读写hdfs脚本,最好是spark的持续读写的计算任务。】
测试更改shuffle包后的影响。

--------------软件准备--------------:
上传到ftp
ncftpput -ubigdata -p'whaley!90365' 10.255.130.6 bigdata/ /home/spark/tmp/hadoop-2.9.0.tar.gz
下载测试
ncftpget -z -ubigdata -p'whaley!90365' 10.255.130.6 /tmp bigdata/hadoop-2.9.0.tar.gz
------------------------------------------

--------------升级步骤--------------:
1.部署hadoop2.9.0
2.安装linux的cgroup服务

--------------部署机器角色--------------：

bigdev-cmpt-1    [namenode1,zk1,                 journalnode]
bigdev-cmpt-2    [namenode2,zk2,resourceManager1,journalnode]
bigdev-cmpt-3    [          zk3,resourceManager2,journalnode]
bigdev-cmpt-4    [nodeManager,datanode]
bigdev-cmpt-5    [nodeManager,datanode]
bigdev-cmpt-6    [nodeManager,datanode]
bigdev-cmpt-7    [nodeManager,datanode]
bigdev-cmpt-8    [nodeManager,datanode]
bigdev-cmpt-9    [nodeManager,datanode]

--------------安装hadoop--------------:
--安装包分发
ansible-playbook -i dev.host install_hadoop-bin_dev_rolling.yml -t install

--配置分发
ansible-playbook -i dev.host install_hadoop-bin_dev_rolling.yml -t config

--------------linux cgroup--------------:
1.安装cgroup
cd /data/tools/ansible/modules/hadoop/playbook
ansible all -i dev.host -mshell -a"yum install -y libcgroup-tools"

2.启动cgroup
ansible all -i dev.host -mshell -a"systemctl start cgconfig.service"

3.查看cgroup服务是否启动成功
ansible all -i dev.host -mshell -a"systemctl status cgconfig.service"

4.创建hadoop-yarn命名的cgroup
ansible all -i dev.host -mshell -a"cd /sys/fs/cgroup/cpu;mkdir -p hadoop-yarn"
查看目录创建是否成功
ansible all -i dev.host -mshell -a"ls -al /sys/fs/cgroup/cpu"

5.改变权限
系统还要求etc/hadoop/container-executor.cfg 的所有父目录(一直到/ 目录) owner 都为 root
  ansible all -i dev.host -mshell -a"cd /app;chown root:hadoop hadoop-2.9.0"
  ansible all -i dev.host -mshell -a"cd /app/hadoop-2.9.0;chown root:hadoop etc"
  ansible all -i dev.host -mshell -a"cd /app/hadoop-2.9.0/etc;chown root:hadoop hadoop"

container-executor权限有特殊要求
  ansible all -i dev.host -mshell -a"cd /app/hadoop-2.9.0/bin;chown root:hadoop container-executor"
  ansible all -i dev.host -mshell -a"cd /app/hadoop-2.9.0;chmod 6050 bin/container-executor"

cgroup权限的更改
  ansible all -i dev.host -mshell -a"cd /sys/fs/cgroup/;chmod 777 cpu,cpuacct"
  ansible all -i dev.host -mshell -a"cd /sys/fs/cgroup/cpu,cpuacct;chmod 777 -R hadoop-yarn"


--------------rolling update--------------:
假设有两个名称节点NN1和NN2，其中NN1和NN2分别处于活动和待机状态。以下是升级HA集群的步骤：
1.准备滚动升级
    1.运行“hdfs dfsadmin -rollingUpgrade prepare”为回滚创建一个fsimage。[在NN1机器上运行]
    2.运行“hdfs dfsadmin -rollingUpgrade query”来检查回滚映像的状态。等待并重新运行该命令，直到显示“继续滚动升级”消息。
2.升级活动和备用NNs
    1.关机并升级NN2。【在NN2机器上,hdfs用户，/opt/hadoop/bin/hadoop-daemon.sh stop namenode】
    2.使用“-rollingUpgrade started”选项启动NN2作为备用。 【hdfs namenode -rollingUpgrade started】
    3.从NN1故障转移到NN2，以便NN2变为活动状态，NN1变为备用namenode状态。
        【在活跃nn上执行，hdfs  haadmin -failover  nn1  nn2】
    4.关机并升级NN1。【在NN1机器上,hdfs用户，/opt/hadoop/bin/hadoop-daemon.sh stop namenode】
    5.使用“-rollingUpgrade started”选项启动NN1作为备用namenode。【hdfs namenode -rollingUpgrade started】
3.升级DNs
    1.选择一小部分数据节点（例如特定机架下的所有数据节点）。
         1.运行“hdfs dfsadmin -shutdownDatanode <DATANODE_HOST：IPC_PORT> upgrade”来关闭所选数据节点之一。
           在nn1节点,hdfs dfsadmin -shutdownDatanode 10.255.129.104:50020 upgrade
         2.运行“hdfs dfsadmin -getDatanodeInfo <DATANODE_HOST：IPC_PORT>”检查并等待datanode关闭。
           在nn1节点,hdfs dfsadmin -getDatanodeInfo 10.255.129.104:50020
         3.升级并重新启动数据节点。[在升级的datanode节点, sh /opt/hadoop/sbin/hadoop-daemon.sh start datanode ]
         4.对子集中所有选定的datanode并行执行上述步骤。
   2.重复上述步骤，直到集群中的所有数据节点都被升级。
4.完成滚动升级
   1.运行“hdfs dfsadmin -rollingUpgrade finalize”来完成滚动升级。




