研发环境安装hadoop2.9.0，用来测试cgroup的可用性


--------------linux cgroup--------------：
1.安装cgroup
cd /data/tools/ansible/modules/hadoop/playbook
ansible all -i dev3.host -mshell -a"yum install -y libcgroup-tools"

2.启动cgroup
ansible all -i dev3.host -mshell -a"systemctl start cgconfig.service"

3.查看cgroup服务是否启动成功
ansible all -i dev3.host -mshell -a"systemctl status cgconfig.service"

4.创建hadoop-yarn命名的cgroup
ansible all -i dev3.host -mshell -a"cd /sys/fs/cgroup/cpu;mkdir -p hadoop-yarn"


ansible all -i dev3.host -mshell -a"ls -al /sys/fs/cgroup/cpu"

5.改变权限
系统还要求etc/hadoop/container-executor.cfg 的所有父目录(一直到/ 目录) owner 都为 root
  ansible all -i dev3.host -mshell -a"cd /opt;chown root:hadoop hadoop"
  ansible all -i dev3.host -mshell -a"cd /opt/hadoop;chown root:hadoop etc"
  ansible all -i dev3.host -mshell -a"cd /opt/hadoop/etc;chown root:hadoop hadoop"
  ansible all -i dev3.host -mshell -a"cd /opt/hadoop/etc/hadoop;chown root:hadoop container-executor.cfg"
  ansible all -i dev3.host -mshell -a"cd /opt/hadoop/etc/hadoop;chmod 755 container-executor.cfg"

container-executor权限有特殊要求
  ansible all -i dev3.host -mshell -a"cd /opt/hadoop/bin;chown root:hadoop container-executor"
  ansible all -i dev3.host -mshell -a"cd /opt/hadoop;chmod 6050 bin/container-executor"

cgroup权限的更改
  ansible all -i dev3.host -mshell -a"cd /sys/fs/cgroup/;chmod 777 cpu,cpuacct"
  ansible all -i dev3.host -mshell -a"cd /sys/fs/cgroup/cpu,cpuacct;chmod 777 -R hadoop-yarn"



--------------软件准备--------------：
上传到ftp
ncftpput -ubigdata -p'whaley!90365' 10.255.130.6 bigdata/ /home/spark/tmp/hadoop-2.9.0.tar.gz
下载测试
ncftpget -z -ubigdata -p'whaley!90365' 10.255.130.6 /tmp bigdata/hadoop-2.9.0.tar.gz


--------------部署机器角色--------------：
bigdev-cmpt-10 [namenode1,zk1,                 journalnode]
bigdev-cmpt-11 [namenode2,zk2,resourceManager1,journalnode]
bigdev-cmpt-12 [          zk3,resourceManager2,journalnode]
bigdev-cmpt-13 [nodeManager]
bigdev-cmpt-14 [nodeManager]
bigdev-cmpt-15 [nodeManager]

--------------安装zookeeper--------------:
modules/zookeeper/readme_dev3.txt

--------------免登录--------------:
ansible-playbook -i dev3.host install_hadoop-bin_dev3.yml -t freessh




--------------安装hadoop--------------:
--安装包分发
ansible-playbook -i dev3.host install_hadoop-bin_dev3.yml -t install

--发布spark shuffle 包
ansible-playbook -i dev3.host install_yarn-spark-shuffle.yml -t install

--配置分发
ansible-playbook -i dev3.host install_hadoop-bin_dev3.yml -t config

--启动journalnode
ansible journalnode -i dev3.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/;sbin/hadoop-daemon.sh start journalnode'"

--tmp operation:
ansible journalnode -i dev3.host -mshell -a"su - hdfs -c  'rm -rf /data/hdfs/journal/hans'"
ansible namenode    -i dev3.host -mshell -a"su - hdfs -c  'rm -rf /data/hdfs/name/*'"
ansible journalnode -i dev3.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/;sbin/hadoop-daemon.sh stop journalnode'"

--格式化hdfs文件系统目录(一定要先启动journalnode)
hadoop namenode -format  [在namenode active节点执行]

hdfs  user
/opt/hadoop/sbin/hadoop-daemon.sh start namenode    [namenode active role]
hdfs namenode -bootstrapStandby  [namenode standby role,for sync info from active role]
/opt/hadoop/sbin/hadoop-daemon.sh start namenode  [namenode standby role]
hdfs zkfc -formatZK [namenode active role]
/opt/hadoop/sbin/start-dfs.sh [namenode active role]

--初始化zkfc根节点
hdfs zkfc -formatZK
#ansible namenode -i dev3.host -mshell -a"su - hdfs -c  'echo Y | hdfs zkfc -formatZK'"

--启动zkfc
ansible namenode -i dev3.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/sbin; ./hadoop-daemon.sh start zkfc'"

--启动hdfs[包含启动datanode,namenode,JournalNode,DFSZKFailoverController]
ansible hadoop-cmd-node -i dev3.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/sbin; ./start-dfs.sh'"

--启动datanode
ansible hadoop-cmd-node -i dev3.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/sbin; ./hadoop-daemon.sh start datanode'"

单台启动
cd /opt/hadoop/sbin; ./hadoop-daemons.sh start datanode

--初始化hdfs目录
ansible hadoop-cmd-node -i dev3.host -mshell -a"su - hdfs -c 'hadoop fs -mkdir -p /tmp/logs/spark && hadoop fs -chmod -R 777 /tmp/logs/spark'"
ansible hadoop-cmd-node -i dev3.host -mshell -a"su - hdfs -c 'hadoop fs -chown -R spark:hadoop /tmp/logs/spark'"
ansible hadoop-cmd-node -i dev3.host -mshell -a"su - hdfs -c 'hadoop fs -setfacl -m group:hadoop:rwx /tmp'"
ansible hadoop-cmd-node -i dev3.host -mshell -a"su - hdfs -c 'hadoop fs -mkdir -p /user && hadoop fs -chmod -R 777 /user'"
ansible hadoop-cmd-node -i dev3.host -mshell -a"su - hdfs -c 'hadoop fs -setfacl -m group:hadoop:rwx /user'"
ansible hadoop-cmd-node -i dev3.host -mshell -a"su - hdfs -c 'hadoop fs -setfacl -m group::r-x /'"
#ansible hadoop-cmd-node -i dev3.host -mshell -a"su - hdfs -c 'hadoop fs -setfacl -m other::r-x /'"

--启动resourcemanager
ansible resourcemanager -i dev3.host -mshell -a"su - yarn -c  'cd /opt/hadoop/sbin; ./yarn-daemon.sh start resourcemanager'"

--启动nodemanager
ansible nodemanager -i dev3.host -mshell -a"su - yarn -c  'cd /opt/hadoop/sbin; ./yarn-daemon.sh start nodemanager'"

--启动historyserver
ansible jobhistoryserver -i dev3.host -mshell -a"su - yarn -c  'cd /opt/hadoop/sbin; ./mr-jobhistory-daemon.sh start historyserver'"

--启动timelineserver
ansible timelineserver -i dev3.host -mshell -a"su - yarn -c  'cd /opt/hadoop/sbin; ./yarn-daemon.sh start timelineserver'"


--------------rolling update--------------:
Upgrading Non-Federated Clusters
假设有两个NameNode NN1和NN2，NN1和NN2分别处在Active和Standby状态。下面是升级一个HA集群的步骤：
1.      准备滚动升级
  1.      运行命令“hdfs dfsadmin -rollingUpgrade prepare”，为滚动创建一个FsImage。
  2.      运行命令“hdfs dfsadmin -rollingUpgrade query”，检查滚动Image的状态。等一会接着重新运行这个命令直到“Proceed with rolling upgrade”消息出现。
2 .升级Active和Standby NNs
  1.      关闭NN2，然后升级NN2
  2.      用“-rollingUpgrade started”选项，启动NN2作为StandbyNameNode。[ hdfs namenode -rollingUpgrade started ]
  3.      从NN1故障转移到NN2，以使NN2处于Active，NN1处于Standby。[ hdfs namenode stop ]
  4.      关闭NN1，然后升级NN1。
  5.      用"rollingUpgrade started”选项，启动NN1作为Standby“。[ hdfs namenode -rollingUpgrade started ]
3 . 升级DNs
  1.      选择一小部分DataNode（所有的DataNode都在一个特定的机架上）。
  1.      运行命令“hdfs dfsadmin -shutdownDatanode <DATANODE_HOST:IPC_PORT> upgrade”，关闭选中的DataNode
  2.      运行命令“hdfs dfsadmin -getDatanodeInfo <DATANODE_HOST:IPC_PORT>”检查等待DataNode关闭
  3.      升级和重新启动DataNode
  4.      在所有选中的机器上运行上边的步骤，一次选中的DataNode可以并行操作。
  2.      重新运行上边的步骤直到集群中的所有DataNode被升级。
4 . 结束滚动升级
  1.      运行“hdfsdfsadmin -rollingUpgrade finalize”结束滚动操作。


参考：
https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/
http://blog.csdn.net/xichenguan/article/details/38752121s


