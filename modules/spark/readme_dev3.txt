
--上传
ncftpput -ubigdata -p'whaley!90365' 10.255.130.6 bigdata/ /home/spark/tmp/spark-2.1.0-bin-hadoop2.7.tgz

--安装包分发
ansible-playbook -i spark.host install_spark-2.1.0_hadoop27.yml -t install

--替换jersey相关jar包
ansible all -i spark.host -mshell -a"mkdir /opt/spark2/bk ; mv /opt/spark2/jars/jersey-client-*.jar /opt/spark2/bk "
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-client-1.9.jar dest=/opt/spark2/jars  owner=spark group=hadoop mode=755"
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-core-1.9.jar dest=/opt/spark2/jars  owner=spark group=hadoop mode=755"

--创建spark event log目录：
ansible historyserver -i spark.host -mshell -a"su - hdfs -c 'hadoop fs -mkdir -p /spark-log/spark-events'"
ansible historyserver -i spark.host -mshell -a"su - hdfs -c 'hadoop fs -chown -R spark:hadoop /spark-log'"

--启动HistoryServer
ansible historyserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark2/sbin && ./start-history-server.sh'"

