此项目包括hdfs、yarn的部署包及其部署脚本

以下功能指令均需在/data/tools/ansible/modules/hadoop/playbook中执行

--安装包分发
ansible-playbook -i hadoop.host install_hadoop-bin.yml -t install

--发布spark shuffle 包
ansible-playbook -i hadoop.host install_yarn-spark-shuffle.yml -t install

--配置分发
ansible-playbook -i hadoop.host install_hadoop-bin.yml -t config

--启动journalnode
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/sbin; ./start-journalnode.sh'"

--格式化hdfs文件系统目录(一定要先启动journalnode)
#以下脚本只可一次执行成功，重复执行需手工到主机上执行，因为重复执行会要多次确认，脚本中的一次echo Y会导致脚本一直等待
#如果导致多次执行，很可能需要手工修正journalnode中的namespace和clusterID
ansible namenode -i hadoop.host -mshell -a"su - hdfs -c  'echo Y | hadoop namenode -format'"

--初始化zkfc根节点
ansible namenode -i hadoop.host -mshell -a"su - hdfs -c  'echo Y | hdfs zkfc -formatZK'"

--启动zkfc
ansible namenode -i hadoop.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/sbin; ./hadoop-daemon.sh start zkfc'"

--启动hdfs
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/sbin; ./start-dfs.sh'"

--启动datanode
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/sbin; ./hadoop-daemons.sh start datanode'"

--初始化hdfs目录
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'hadoop fs -mkdir -p /tmp/logs/spark && hadoop fs -chmod -R 777 /tmp/logs/spark'"
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'hadoop fs -chown -R spark:hadoop /tmp/logs/spark'
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c 'hadoop fs -setfacl -m group:hadoop:rwx /tmp'"
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c 'hadoop fs -setfacl -m group:hadoop:rwx /user'"
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c 'hadoop fs -setfacl -m group::r-x /'"
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c 'hadoop fs -setfacl -m other::r-x /'"


--启动resourcemanager
JMX_OPTS="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=7778 -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false"
ansible resourcemanager -i hadoop.host -mshell -a"su - yarn -c  'export JMX_OPTS=$JMX_OPTS ; cd /opt/hadoop/sbin; ./yarn-daemon.sh start resourcemanager'"

--启动nodemanager
JMX_OPTS="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=7777 -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false"
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - yarn -c  'export JMX_OPTS=$JMX_OPTS ; cd /opt/hadoop/sbin; ./yarn-daemons.sh start nodemanager'"

--启动historyserver
ansible jobhistoryserver -i hadoop.host -mshell -a"su - yarn -c  'cd /opt/hadoop/sbin; ./mr-jobhistory-daemon.sh start historyserver'"

--启动timelineserver
ansible timelineserver -i hadoop.host -mshell -a"su - yarn -c  'export jmxPort=7779; cd /opt/hadoop/sbin; ./yarn-daemon.sh start timelineserver'"


--停止zkfc
ansible namenode -i hadoop.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/sbin; ./hadoop-daemon.sh stop zkfc'"

--停止journalnode
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/sbin; ./stop-journalnode.sh'"

--停止hdfs
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/sbin; ./stop-dfs.sh'"

--停止datanode
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'cd /opt/hadoop/sbin; ./hadoop-daemons.sh stop datanode'"


--停止resourcemanager
ansible resourcemanager -i hadoop.host -mshell -a"su - yarn -c  'cd /opt/hadoop/sbin; ./yarn-daemon.sh stop resourcemanager'"

--停止nodemanager
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - yarn -c  'cd /opt/hadoop/sbin; ./yarn-daemons.sh stop nodemanager'"

--停止historyserver
ansible jobhistoryserver -i hadoop.host -mshell -a"su - yarn -c  'cd /opt/hadoop/sbin; ./mr-jobhistory-daemon.sh stop historyserver'"

--停止timelineserver
ansible timelineserver -i hadoop.host -mshell -a"su - yarn -c  'cd /opt/hadoop/sbin; ./yarn-daemon.sh stop timelineserver'"



--刷新scheduler配置
ansible all -i hadoop.host -mcopy -a"src=/data/tools/ansible/modules/hadoop/config/etc/hadoop/fair-scheduler.xml dest=/opt/hadoop/etc/hadoop  owner=hadoop group=hadoop mode=755"
ansible resourcemanager -i hadoop.host -mshell -a"su - yarn -c  'yarn rmadmin -refreshQueues'"

--刷新HDFS节点
ansible all -i hadoop.host -mcopy -a"src=/data/tools/ansible/modules/hadoop/config/etc/hadoop/yarn-site.xml dest=/opt/hadoop/etc/hadoop  owner=hadoop group=hadoop mode=755"
ansible all -i hadoop.host -mcopy -a"src=/data/tools/ansible/modules/hadoop/config/etc/hadoop/core-site.xml dest=/opt/hadoop/etc/hadoop  owner=hadoop group=hadoop mode=755"
ansible all -i hadoop.host -mcopy -a"src=/data/tools/ansible/modules/hadoop/config/etc/hadoop/excludes dest=/opt/hadoop/etc/hadoop  owner=hadoop group=hadoop mode=755"
ansible all -i hadoop.host -mcopy -a"src=/data/tools/ansible/modules/hadoop/config/etc/hadoop/slaves dest=/opt/hadoop/etc/hadoop  owner=hadoop group=hadoop mode=755"

ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - yarn -c  'yarn rmadmin -refreshNodes'"
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'hdfs dfsadmin -refreshNodes'"
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'hdfs dfsadmin -report'"

--metrics配置分发
ansible all -i hadoop.host -mcopy -a"src=/data/tools/ansible/modules/hadoop/config/etc/hadoop/hadoop-metrics2.properties dest=/opt/hadoop/etc/hadoop  owner=hadoop group=hadoop mode=755"



ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'hdfs fsck / -blocks -locations -files'|grep 128-49"
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'nohup hdfs balancer -threshold 2 &'"
ansible hadoop-cmd-node -i hadoop.host -mshell -a"su - hdfs -c  'hdfs fsck / -files -blocks -racks'

hdfs fsck -openforwrite  /
hdfs fsck -openforwrite  /|grep "10.255.128.39"|awk '{print $1}'|sort|uniq|awk -F ':' '{print "hadoop fs -rm -r "$1}'
/user/hdfs/.Trash/Current/tmp/hadoop/yarn/timeline/generic-history/ApplicationHistoryDataRoot/application_1487994926980_0093


#guava库替换
ansible-playbook -i hadoop.host install_guava.yml -t install
ansible-playbook -i hadoop.host install_guava.yml -t rollback
ansible-playbook -i hadoop.host install_guava.yml -t upgrade

ansible all -i hadoop.host -mshell -a"rm -f /opt/hadoop/share/hadoop/common/lib/guava.jar && ln -s /opt/hadoop/share/hadoop/common/lib/guava-18.0.jar.bk /opt/hadoop/share/hadoop/common/lib/guava.jar"

ansible all -i hadoop.host -mshell -a"ls -al /opt/hadoop/share/hadoop/common/lib/guava*"
ansible all -i hadoop.host -mshell -a"ls -al /opt/hadoop/share/hadoop/hdfs/lib/guava*"
ansible all -i hadoop.host -mshell -a"ls -al /opt/hadoop/share/hadoop/tools/lib/guava*"
ansible all -i hadoop.host -mshell -a"ls -al /opt/hadoop/share/hadoop/yarn/lib/guava*"
ansible all -i hadoop.host -mshell -a"ls -al /opt/hadoop/share/hadoop/httpfs/tomcat/webapps/webhdfs/WEB-INF/lib/guava*"
ansible all -i hadoop.host -mshell -a"ls -al /opt/hadoop/share/hadoop/kms/tomcat/webapps/kms/WEB-INF/lib/guava*"


-------------------hadoop分发给云主机的模版机器-------------------
cd /data/tools/ansible/modules/hadoop/playbook
--安装包分发
ansible-playbook -i hadoop-template.host install_hadoop-bin.yml -t install

--发布spark shuffle 包
ansible-playbook -i hadoop-template.host install_yarn-spark-shuffle.yml -t install

--配置分发
ansible-playbook -i hadoop-template.host install_hadoop-bin.yml -t config



=======================namenode备份==========================
--脚本分发&设置crontab
ansible-playbook -i hadoop.host install_hadoop-bin.yml -t backup