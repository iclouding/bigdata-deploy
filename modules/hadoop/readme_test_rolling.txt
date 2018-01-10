测试环境滚动升级hadoop2.6.3到hadoop2.9.0，并启cgroup机制。
用来测试升级过程中不影响线上服务以及cgroup的可用性。

测试点：
测试hdfs在升级过程一直可用。【编写持续读写hdfs脚本,最好是spark的持续读写的计算任务。】
测试更改shuffle包后的影响。
测试hbase的影响范围[编写持续读写脚本]

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

10.255.129.18    [namenode1,zk1,                 journalnode]
10.255.129.19    [namenode2,zk2,resourceManager1,journalnode,jobhistoryserver]
10.255.129.20    [          zk3,resourceManager2,journalnode,timelineserver]
10.255.129.201   [nodeManager,datanode,cgourp service]
10.255.129.202   [nodeManager,datanode,cgourp service]
10.255.129.203   [nodeManager,datanode,cgourp service]
10.255.129.204   [nodeManager,datanode,cgourp service]
10.255.129.205   [nodeManager,datanode,cgourp service]

10.255.129.1 ... 10.255.129.9  [app server]


--------------安装hadoop--------------:
--安装包分发
ansible-playbook -i test_rolling.host install_hadoop-bin_test_rolling.yml -t install

--配置分发
ansible-playbook -i test_rolling.host install_hadoop-bin_test_rolling.yml -t config
ansible-playbook -i test_rolling.host install_hadoop-bin_test_rolling.yml -t ranger_config

--------------linux cgroup--------------:
1.安装cgroup
cd /data/tools/ansible/modules/hadoop/playbook
ansible cgroup -i test_rolling.host -mshell -a"yum install -y libcgroup libcgroup-tools"

2.启动cgroup
ansible cgroup -i test_rolling.host -mshell -a"systemctl start cgconfig.service"
关闭：
ansible cgroup -i test_rolling.host -mshell -a"systemctl stop cgconfig.service"


3.查看cgroup服务是否启动成功
ansible cgroup -i test_rolling.host -mshell -a"systemctl status cgconfig.service"

4.创建hadoop-yarn命名的cgroup[启动服务后，创建目录]
ansible cgroup -i test_rolling.host -mshell -a"cd /sys/fs/cgroup/cpu;mkdir -p hadoop-yarn"
查看目录创建是否成功
ansible cgroup -i test_rolling.host -mshell -a"ls -al /sys/fs/cgroup/cpu/hadoop-yarn"

5.改变权限[等待安装完hadoop后操作]
系统还要求etc/hadoop/container-executor.cfg 的所有父目录(一直到/ 目录) owner 都为 root
  ansible cgroup -i test_rolling.host -mshell -a"cd /app;chown root:hadoop hadoop-2.9.0"
  ansible cgroup -i test_rolling.host -mshell -a"cd /app/hadoop-2.9.0;chown root:hadoop etc"
  ansible cgroup -i test_rolling.host -mshell -a"cd /app/hadoop-2.9.0/etc;chown root:hadoop hadoop"

container-executor权限有特殊要求
  ansible cgroup -i test_rolling.host -mshell -a"cd /app/hadoop-2.9.0/bin;chown root:hadoop container-executor"
  ansible cgroup -i test_rolling.host -mshell -a"cd /app/hadoop-2.9.0;chmod 6050 bin/container-executor"

cgroup权限的更改[测试环境，刚才all host执行5步骤]
  ansible cgroup -i test_rolling.host -mshell -a"cd /sys/fs/cgroup/;chmod 777 cpu,cpuacct"
  ansible cgroup -i test_rolling.host -mshell -a"cd /sys/fs/cgroup/cpu,cpuacct;chmod 777 -R hadoop-yarn"
  检测：
  ansible cgroup -i test_rolling.host -mshell -a"ls -al /sys/fs/cgroup/cpu,cpuacct "
  ansible cgroup -i test_rolling.host -mshell -a"ls -al /sys/fs/cgroup "


--------------rolling update--------------:
hdfs@bigtest-appsvr-129-1,/home/hdfs/fsimage_backup目录，备份fsimage镜像
执行 hdfs dfsadmin  -fetchImage  .
或者
到namenode active节点，/data/hdfs/name/current目录,拷贝最新的镜像，例如，fsimage_0000000000050828706

假设有两个名称节点NN1和NN2，其中NN1和NN2分别处于活动和待机状态。以下是升级HA集群的步骤：
1.准备滚动升级
    1.运行“hdfs dfsadmin -rollingUpgrade prepare”为回滚创建一个fsimage。[在NN1机器上运行]
       ansible nn1 -i test_rolling.host -mshell -a"su - hdfs -c 'hdfs dfsadmin -rollingUpgrade prepare' "
       会在nn1机器上，/data/hdfs/name/current目录，生成fsimage_rollback_0000000000050847217，用于回滚。
    2.运行“hdfs dfsadmin -rollingUpgrade query”来检查回滚映像的状态。等待并重新运行该命令，直到显示“继续滚动升级”消息。
       ansible nn1 -i test_rolling.host -mshell -a"su - hdfs -c 'hdfs dfsadmin -rollingUpgrade query' "
       当显示"Proceed with rolling upgrade"信息时，继续执行下面步骤。
2.升级活动和备用NNs
    1.关机并升级NN2。
        关机:a.验证nn2是否是standby nn
            b. ansible nn2 -i test_rolling.host -mshell -a"su - hdfs -c '/opt/hadoop/sbin/hadoop-daemon.sh stop namenode'"
        升级standby NN
        ansible nn2 -i test_rolling.host -mshell -a"rm -f /opt/hadoop;ln -s /app/hadoop-2.9.0 /opt/hadoop;chown -h hadoop:hadoop /opt/hadoop"
    2.使用“-rollingUpgrade started”选项启动NN2作为备用。
       ansible nn2 -i test_rolling.host -mshell -a"su - hdfs -c 'hdfs namenode -rollingUpgrade started'"
       使用下面命令，一直等待没有返回结果，强制ctrl+c退出，不是一个好的方式，但namenode进程仍然在nn2存在。
       不要在nn2机器上执行hdfs namenode -rollingUpgrade started，会打日志到控制台.
    3.从NN1故障转移到NN2，以便NN2变为活动状态，NN1变为备用namenode状态。[注意：当前10.255.129.101为standby,所以failover后的参数需要调整]
         failover后面的参数nn1,nn2需要从hdfs-site.xml文件中查找，而不是test_rolling.host中配置的nn1,nn2.
         从hdfs-site.xml文件得知,nn1为bigtest-cmpt-129-18,nn2为bigtest-cmpt-129-19。
         （hdfs-site.xml范围）目前nn2为active，nn1为standby，并期望将nn1变为active
         ansible nn1 -i test_rolling.host -mshell -a"su - hdfs -c 'hdfs  haadmin -failover nn2 nn1'"
         得到结果"Failover to NameNode at bigtest-cmpt-129-18/10.255.129.18:9000 successful"
    4.关机并升级NN1。
      ansible nn1 -i test_rolling.host -mshell -a"su - hdfs -c '/opt/hadoop/sbin/hadoop-daemon.sh stop namenode'"
      ansible nn1 -i test_rolling.host -mshell -a"rm -f /opt/hadoop;ln -s /app/hadoop-2.9.0 /opt/hadoop;chown -h hadoop:hadoop /opt/hadoop"
    5.使用“-rollingUpgrade started”选项启动NN1作为备用namenode。
      在nn1机器上执行hdfs namenode -rollingUpgrade started
      不用【ansible nn1 -i test_rolling.host -mshell -a"su - hdfs -c 'hdfs namenode -rollingUpgrade started'"】命令
    6.升级ResourceManager节点[等namenode和datanode节点都升级完成，再操作.TODO]
      a.到没有和namenode相重合的ResourceManager节点，例如rm1，但发现rm1为active节点，所以先重启rm2节点
        ansible rm2 -i test_rolling.host -mshell -a"su - yarn -c '/opt/hadoop/sbin/yarn-daemon.sh stop  resourcemanager'"
        ansible rm2 -i test_rolling.host -mshell -a"su - yarn -c '/opt/hadoop/sbin/yarn-daemon.sh start resourcemanager'"
        然后，对rm1切换软连接，并且重启
        ansible rm1 -i test_rolling.host -mshell -a"su - yarn -c '/opt/hadoop/sbin/yarn-daemon.sh stop resourcemanager'"
        ansible rm1 -i test_rolling.host -mshell -a"rm -f /opt/hadoop;ln -s /app/hadoop-2.9.0 /opt/hadoop;chown -h hadoop:hadoop /opt/hadoop"
        ansible rm1 -i test_rolling.host -mshell -a"su - yarn -c '/opt/hadoop/sbin/yarn-daemon.sh start resourcemanager'"
      b.重启node manager节点,yarn用户
        ansible rm2 -i test_rolling.host -mshell -a"su - yarn -c '/opt/hadoop/sbin/yarn-daemons.sh start  nodemanager'"
    7.升级app server节点[等namenode和datanode节点都升级完成，再操作.TODO]
    ansible appserver -i test_rolling.host -mshell -a"rm -f /opt/hadoop;ln -s /app/hadoop-2.9.0 /opt/hadoop;chown -h hadoop:hadoop /opt/hadoop"
    8.重启ApplicationHistoryServer和JobHistoryServer[等namenode和datanode节点都升级完成，再操作.TODO]
3.升级DNs
    1.选择一小部分数据节点（例如特定机架下的所有数据节点，hdfs dfsadmin -printTopology）。
         1.运行“hdfs dfsadmin -shutdownDatanode <DATANODE_HOST：IPC_PORT> upgrade”来关闭所选数据节点之一。
           在nn2节点【这个时候已经成为了active】,hdfs dfsadmin -shutdownDatanode 10.255.129.104:50020 upgrade
           ansible nn2 -i test_rolling.host -mshell -a"su - hdfs -c 'hdfs dfsadmin -shutdownDatanode 10.255.129.204:50020 upgrade'"
           ansible nn2 -i test_rolling.host -mshell -a"su - hdfs -c 'hdfs dfsadmin -shutdownDatanode 10.255.129.205:50020 upgrade'"
         2.运行“hdfs dfsadmin -getDatanodeInfo <DATANODE_HOST：IPC_PORT>”检查并等待datanode关闭。
           在nn2节点,hdfs dfsadmin -getDatanodeInfo 10.255.129.204:50020
           在nn2节点,hdfs dfsadmin -getDatanodeInfo 10.255.129.205:50020
           ansible nn2 -i test_rolling.host -mshell -a"su - hdfs -c 'hdfs dfsadmin -getDatanodeInfo 10.255.129.104:50020 '"
           返回结果是java.net.ConnectException，表示datanode已经关闭
         3.升级并重新启动数据节点
           roll_tmp_datanode.host 临时文件内容为：
           [all]
           10.255.129.204
           10.255.129.205
           升级的datanode节点:
           ansible all -i roll_tmp_datanode.host -mshell -a"rm -f /opt/hadoop;ln -s /app/hadoop-2.9.0 /opt/hadoop;chown -h hadoop:hadoop /opt/hadoop"
           启动datanode节点:
           ansible all -i roll_tmp_datanode.host -mshell -a"su - hdfs -c '/opt/hadoop/sbin/hadoop-daemon.sh start datanode'"
           检测：
           ansible all -i roll_tmp_datanode.host -mshell -a"su - hdfs -c 'jps'"
         4.对子集中所有选定的datanode并行执行上述步骤。
            第一轮：
                    roll_tmp_datanode.host 临时文件内容为：
                    [all]
                    10.255.129.201
                    10.255.129.202
                    10.255.129.203
                   关闭所选数据节点:
                     ansible all -i roll_tmp_datanode.host -mshell -a"su - hdfs -c 'hdfs dfsadmin -shutdownDatanode localhost:50020 upgrade'"
                   检查并等待datanode关闭:
                     ansible all -i roll_tmp_datanode.host -mshell -a"su - hdfs -c 'hdfs dfsadmin -getDatanodeInfo localhost:50020'"
                   升级的datanode节点:
                     ansible all -i roll_tmp_datanode.host -mshell -a"rm -f /opt/hadoop;ln -s /app/hadoop-2.9.0 /opt/hadoop;chown -h hadoop:hadoop /opt/hadoop"
                   启动datanode节点:
                     ansible all -i roll_tmp_datanode.host -mshell -a"su - hdfs -c '/opt/hadoop/sbin/hadoop-daemon.sh start datanode'"
            第二轮：
                    roll_tmp_datanode.host 临时文件内容为：[每个机架的机器作为一个子集，进行关闭，防止同事关闭datanode数量超过3时，client不能读取部分块数据]
                    [all]
                    10.255.129.107x
                    10.255.129.108x
                    10.255.129.109x
                   关闭所选数据节点:
                     ansible all -i roll_tmp_datanode.host -mshell -a"su - hdfs -c 'hdfs dfsadmin -shutdownDatanode localhost:50020 upgrade'"
                   检查并等待datanode关闭:
                     ansible all -i roll_tmp_datanode.host -mshell -a"su - hdfs -c 'hdfs dfsadmin -getDatanodeInfo localhost:50020'"
                   升级的datanode节点:
                     ansible all -i roll_tmp_datanode.host -mshell -a"rm -f /opt/hadoop;ln -s /app/hadoop-2.9.0 /opt/hadoop;chown -h hadoop:hadoop /opt/hadoop"
                   启动datanode节点:
                     ansible all -i roll_tmp_datanode.host -mshell -a"su - hdfs -c '/opt/hadoop/sbin/hadoop-daemon.sh start datanode'"

   2.重复上述步骤，直到集群中的所有数据节点都被升级。
4.完成滚动升级
   1.【等待一周后、没有发现问题再执行finalize命令，否则影响降级和回滚】
     【等一周、确认升级无误】运行“hdfs dfsadmin -rollingUpgrade finalize”来完成滚动升级。
     【等一周、确认升级无误】ansible nn2 -i test_rolling.host -mshell -a"su - hdfs -c 'hdfs dfsadmin -rollingUpgrade finalize'"


--------------其他--------------:
1.rollingUpgrade进程存在问题：
通过hdfs namenode -rollingUpgrade started命令启动namenode后，
namenode的进程变成org.apache.hadoop.hdfs.server.namenode.NameNode -rollingUpgrade started
并且通过ansible远程执行这个命令，ctrl+c防止终端，虽然在管理机报错，但是没有关系，namenode进程本身已经启动。
如果想要关闭此种类型的namenode进程，需要在/data/logs/hadoop-hdfs位置，hadoop-hdfs-namenode.pid文件中写入当前namenode的进程号，
然后通过在namenode节点，使用/opt/hadoop/sbin/hadoop-daemon.sh stop namenode来关闭namenode.

2.常用命令
a.重启所有node manager[需要在RM上执行]
    sh /opt/hadoop/sbin/yarn-daemon.sh stop resourcemanager
    sh /opt/hadoop/sbin/yarn-daemon.sh start resourcemanager
b.重启所有node manager[需要在RM上执行]
    sh /opt/hadoop/sbin/yarn-daemons.sh stop   nodemanager
    sh /opt/hadoop/sbin/yarn-daemons.sh start  nodemanager
c.重启ApplicationHistoryServer
    sh /opt/hadoop/sbin/yarn-daemon.sh stop  timelineserver
    sh /opt/hadoop/sbin/yarn-daemon.sh start timelineserver
d.重启JobHistoryServer[yarn用户]
    sh /opt/hadoop/sbin/mr-jobhistory-daemon.sh stop  historyserver
    sh /opt/hadoop/sbin/mr-jobhistory-daemon.sh start historyserver
e.更新yarn-site.xml文件，调节cpu负载值
ansible all -i test_rolling.host -mcopy -a"src=/data/tools/ansible/modules/hadoop/config_dev_rolling/etc/hadoop/yarn-site.xml dest=/opt/hadoop/etc/hadoop  owner=hadoop group=hadoop mode=755"
以yarn用户,
到standby resource manager机器重启resourcemanager，然后到active resource manager机器重启resourcemanager
重启nodemanager，
ansible nodemanager -i test_rolling.host -mshell -a"su - yarn -c '/opt/hadoop/sbin/yarn-daemon.sh stop  nodemanager'"
ansible nodemanager -i test_rolling.host -mshell -a"su - yarn -c '/opt/hadoop/sbin/yarn-daemon.sh start nodemanager'"
f.yarn的其他两个demon服务
jps
ApplicationHistoryServer ->  timeline             /opt/hadoop/sbin/yarn-daemon.sh start timelineserver          [yarn]
JobHistoryServer         -> JobHistoryServer      /opt/hadoop/sbin//mr-jobhistory-daemon.sh start historyserver [yarn]
g.检测特定文件夹只能够文件块是否损坏
hdfs fsck --help
3/user/spark/
hdfs fsck -list-corruptfileblocks /user/spark/
hdfs fsck -delete /user/spark/.sparkStaging/application_1513602413357_0134/__spark_libs__7578766376575669211.zip

--------------------------------启动停止命令--------------------------------
启动停止全部datanode
ansible nn1 -i test_rolling.host -mshell -a"su - hdfs -c 'sh /opt/hadoop/sbin/hadoop-daemons.sh stop datanode'"
ansible nn1 -i test_rolling.host -mshell -a"su - hdfs -c 'sh /opt/hadoop/sbin/hadoop-daemons.sh start datanode'"

滚动启动namenode
ansible nn1 -i test_rolling.host -mshell -a"su - hdfs -c 'hdfs namenode -rollingUpgrade started'"
ansible nn2 -i test_rolling.host -mshell -a"su - hdfs -c 'hdfs namenode -rollingUpgrade started'"

启动停止resourcemanager
ansible rm1 -i test_rolling.host -mshell -a"su - yarn -c '/opt/hadoop/sbin/yarn-daemon.sh start resourcemanager'"
ansible rm1 -i test_rolling.host -mshell -a"su - yarn -c '/opt/hadoop/sbin/yarn-daemon.sh start resourcemanager'"
ansible rm1 -i test_rolling.host -mshell -a"su - yarn -c '/opt/hadoop/sbin/yarn-daemon.sh stop resourcemanager'"
ansible rm2 -i test_rolling.host -mshell -a"su - yarn -c '/opt/hadoop/sbin/yarn-daemon.sh stop resourcemanager'"

启动停止全部nodemanager
ansible rm2 -i test_rolling.host -mshell -a"su - yarn -c 'sh /opt/hadoop/sbin/yarn-daemons.sh start nodemanager'"
ansible rm2 -i test_rolling.host -mshell -a"su - yarn -c 'sh /opt/hadoop/sbin/yarn-daemons.sh stop  nodemanager'"

正常启动停止namenode
ansible nn1 -i test_rolling.host -mshell -a"su - hdfs -c '/opt/hadoop/sbin/hadoop-daemon.sh stop  namenode'"
ansible nn2 -i test_rolling.host -mshell -a"su - hdfs -c '/opt/hadoop/sbin/hadoop-daemon.sh stop  namenode'"
ansible nn1 -i test_rolling.host -mshell -a"su - hdfs -c '/opt/hadoop/sbin/hadoop-daemon.sh start namenode'"
ansible nn2 -i test_rolling.host -mshell -a"su - hdfs -c '/opt/hadoop/sbin/hadoop-daemon.sh start namenode'"


--------------------------------查看服务是否正常--------------------------------
查看datanode是否正常
ansible nodemanager -i test_rolling.host -mshell -a"su - hdfs -c 'jps'"
查看node manager是否正常
ansible nodemanager -i test_rolling.host -mshell -a"su - yarn -c 'jps'"
查看namenode是否正常
ansible namenode -i test_rolling.host -mshell -a"su - hdfs -c 'jps'"
查看resource manager是否正常
ansible resourcemanager -i test_rolling.host -mshell -a"su - yarn -c 'jps'"
查看journalnode是否正常
ansible journalnode -i test_rolling.host -mshell -a"su - hdfs -c 'jps'"
查看JobHistoryServer是否正常
ansible jobhistoryserver -i test_rolling.host -mshell -a"su - yarn -c 'jps'"
查看JobHistoryServer是否正常
ansible timelineserver -i test_rolling.host -mshell -a"su - yarn -c 'jps'"
