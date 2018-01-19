研发环境回退到hadoop2.6.2，与线上保持一致

--------------部署机器角色--------------：
10.255.129.18    [namenode1,zk1,                 journalnode]
10.255.129.19    [namenode2,zk2,resourceManager1,journalnode,jobhistoryserver]
10.255.129.20    [          zk3,resourceManager2,journalnode,timelineserver]
10.255.129.201   [nodeManager,datanode,cgourp service]
10.255.129.202   [nodeManager,datanode,cgourp service]
10.255.129.203   [nodeManager,datanode,cgourp service]
10.255.129.204   [nodeManager,datanode,cgourp service]
10.255.129.205   [nodeManager,datanode,cgourp service]

10.255.129.1 ... 10.255.129.9  [app server]

--------------------------------------------hdfs启动过程 --------------------------------------------
--启动journalnode
ansible journalnode -i dev3.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/;sbin/hadoop-daemon.sh start journalnode'"

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


--初始化hdfs目录
hadoop fs -mkdir -p /tmp/logs/spark && hadoop fs -chmod -R 777 /tmp/logs/spark
hadoop fs -chown -R spark:hadoop /tmp/logs/spark
hadoop fs -setfacl -m group:hadoop:rwx /tmp
hadoop fs -mkdir -p /user && hadoop fs -chmod -R 777 /user
hadoop fs -setfacl -m group:hadoop:rwx /user
hadoop fs -setfacl -m group::r-x /
hadoop fs -setfacl -m other::r-x /

