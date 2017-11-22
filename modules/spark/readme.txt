此项目包括spark standalone相关的部署包及其部署脚本
PS:下文中提到的“节点”，都可以在playbook/spark.host中找到

--安装包分发
ansible-playbook -i spark.host install_spark-1.6.3.yml -t install

--配置分发
ansible-playbook -i spark.host install_spark-1.6.3.yml -t config

--创建hdfs目录，上传assembly包到hdfs
ansible-playbook -i spark.host install_spark-1.6.3.yml -t hdfs

--启动spark-standalone集群
ansible master -i spark.host -mshell -a"su - spark -c 'cd /opt/spark/sbin && ./start-all.sh'"

--启动HistoryServer
ansible historyserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark/sbin && ./start-history-server.sh'"

--启动Thriftserver
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/config/spark1.6.3/conf/spark-thrift-sparkconf.conf dest=/opt/spark/conf  owner=spark group=hadoop mode=755"
ansible thriftserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark && ./sbin/launch-thriftserver.sh'"


--停止spark-standalone集群
ansible master -i spark.host -mshell -a"su - spark -c 'cd /opt/spark/sbin && ./stop-all.sh'"

--停止HistoryServer
ansible historyserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark/sbin && ./stop-history-server.sh'"

--停止Thriftserver
ansible thriftserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark && ./sbin/stop-thriftserver.sh'"


人工安装部署步骤：
1.按照spark.host文件中定义的主机进行分发tar包和配置文件（master和worker都需要分发）
2.在master节点【bigdata-cmpt-128-13】上,以spark用户执行$SPARK_HOME/sbin/start-all.sh，启动spark集群
3.在historyserver节点【bigdata-cmpt-128-25】上,以spark用户执行$SPARK_HOME/sbin/start-history-server.sh，启动HistoryServer

启动前准备：
1.创建hdfs相关目录：
    1.1创建spark event log目录：
        su - hdfs
        hadoop fs -mkdir -p /spark-log/spark-events
        hadoop fs -chown -R spark:hadoop /spark-log
    1.2创建lib目录/libs/common(如果已存在则直接使用)
        su - hdfs
        hadoop fs -mkdir -p /libs/common
        hadoop fs -chown -R spark:hadoop /libs/common
2.上传spark assembly jar
        su - spark
        hadoop fs -put /opt/spark/lib/spark-assembly-1.6.3-hadoop2.6.2.jar /libs/common

 
启动集群：
    1.在[master]节点启动spark standalone模式：
        su - spark
        cd /opt/spark/sbin
        ./start-all.sh

    2.在[historyserver]节点启动HistoryServer
        su - spark
        cd /opt/spark/sbin
        ./start-history-server.sh
        3.在[thriftserver]各节点上启动HiveThriftServer2
        su - spark
        cd /opt/spark/
        sbin/start-thriftserver.sh --properties-file conf/spark-thrift-sparkconf.conf



-==================spark2.1.0==============================
--安装包分发
ansible-playbook -i spark.host install_spark-2.1.0.yml -t install

--配置分发
ansible-playbook -i spark.host install_spark-2.1.0.yml -t config
ansible-playbook -i spark.host install_spark-2.1.0.yml -t config_launch


--替换jersey相关jar包
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-client-1.9.jar dest=/opt/spark2/jars  owner=spark group=hadoop mode=755"
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-core-1.9.jar dest=/opt/spark2/jars  owner=spark group=hadoop mode=755"
ansible all -i spark.host -mshell -a"mkdir /opt/spark2/bk ; mv /opt/spark2/jars/jersey-client-*.jar /opt/spark2/bk ;  mv /opt/spark2/jars/jersey-core-*.jar /opt/spark2/bk"

启动spark thrift server
 --root用户
 ansible thriftserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark2 && ./sbin/launch-thriftserver.sh'"
 --spark用户
 ansible thriftserver -i spark.host -mshell -a"cd /opt/spark2 && ./sbin/launch-thriftserver.sh"
 停止Thriftserver
 ansible thriftserver -i spark.host -mshell -a"cd /opt/spark2 && ./sbin/stop-thriftserver.sh"

==================spark2.2.0==============================
--安装包分发
ansible-playbook -i spark2.2.0.host install_spark-2.2.0.yml -t install

--配置分发
ansible-playbook -i spark2.2.0.host install_spark-2.2.0.yml -t config
因为目前最新spark2.2.0仍然依赖hive1.2.1来做元数据管理，为了做如下jar包替换
ansible all -i spark2.2.0.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-client-1.9.jar dest=/opt/spark220/jars  owner=spark group=hadoop mode=755"
ansible all -i spark2.2.0.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-core-1.9.jar dest=/opt/spark220/jars  owner=spark group=hadoop mode=755"
ansible all -i spark2.2.0.host -mshell -a"mkdir /opt/spark220/bk ; mv /opt/spark220/jars/jersey-client-*.jar /opt/spark220/bk ;  mv /opt/spark220/jars/jersey-core-*.jar /opt/spark220/bk"

--spark thrift server 操作
1.启动
  ansible thriftserver -i spark2.2.0.host -mshell -a"su - spark -c 'cd /opt/spark220 && ./sbin/launch-thriftserver.sh'"
2.停止
  ansible thriftserver -i spark.host -mshell -a"cd /opt/spark2 && ./sbin/stop-thriftserver.sh"
  如果通过上面命令，停止不了，通过下面命令强制杀掉进程
  ansible thriftserver -i spark.host -mshell -a "ps -ef|grep HiveThriftServer2 |grep 20360 | grep -v 'grep' | awk '{print \$2}' |xargs kill -9  "




