
----------------------------------------spark 滚动升级步骤 测试环境----------------------------------------
--上传
ncftpput -ubigdata -p'whaley!90365' 10.255.130.6 bigdata/ /home/hadoop/build_home/tmp/spark-2.1.2-bin-hadoop2.9.0.tgz
ncftpput -ubigdata -p'whaley!90365' 10.255.130.6 bigdata/ /home/hadoop/build_home/spark-2.2.1/spark-2.2.1-bin-hadoop2.9.0.tgz

-----------------spark-2.1.2-bin-hadoop2.9.0-----------------
--安装包分发
cd /data/tools/ansible/modules/spark/playbook_test
ansible-playbook -i spark.host install_spark-2.1.2_hadoop29.yml -t install
ansible-playbook -i spark.host install_spark-2.1.2_hadoop29.yml -t spark212_hadoop29_test_config

--替换jersey相关jar包
cd /data/tools/ansible/modules/spark/playbook_test
ansible all -i spark.host -mshell -a"mkdir /app/spark-2.1.2-bin-hadoop2.9.0/bk ; mv /app/spark-2.1.2-bin-hadoop2.9.0/jars/jersey-client-*.jar /app/spark-2.1.2-bin-hadoop2.9.0/bk "
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-client-1.9.jar dest=/app/spark-2.1.2-bin-hadoop2.9.0/jars  owner=spark group=hadoop mode=755"
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-core-1.9.jar dest=/app/spark-2.1.2-bin-hadoop2.9.0/jars  owner=spark group=hadoop mode=755"

--重启HistoryServer【在正式切换的时候操作】
1.关闭HistoryServer
ansible historyserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark2/sbin && ./stop-history-server.sh'"
2.切换软连接
ansible all -i spark.host -mshell -a"rm -f /opt/spark2;ln -s /app/spark-2.1.2-bin-hadoop2.9.0 /opt/spark2;chown -h spark:hadoop /opt/spark2"
3.启动HistoryServer
ansible historyserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark2/sbin && ./start-history-server.sh'"

--更新spark-2.1.2-yarn-shuffle文件
ansible all -i spark.host -mshell -a"cd /opt/hadoop/share/hadoop/yarn;ln -s -f /opt/spark2/yarn/spark-2.1.2-yarn-shuffle.jar spark-yarn-shuffle.jar;chown -h hadoop:hadoop spark-yarn-shuffle.jar"
重启resourcemanager，nodemanager
测试spark shuffle是否正常

-----------------spark-2.2.1-bin-hadoop2.9.0-----------------
--安装包分发
cd /data/tools/ansible/modules/spark/playbook_test
ansible-playbook -i spark.host install_spark-2.2.1_hadoop29.yml -t install
ansible-playbook -i spark.host install_spark-2.2.1_hadoop29.yml -t spark221_hadoop29_test_config
--替换jersey相关jar包
ansible all -i spark.host -mshell -a"mkdir /app/spark-2.2.1-bin-hadoop2.9.0/bk ; mv /app/spark-2.2.1-bin-hadoop2.9.0/jars/jersey-client-*.jar /app/spark-2.2.1-bin-hadoop2.9.0/bk "
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-client-1.9.jar dest=/app/spark-2.2.1-bin-hadoop2.9.0/jars  owner=spark group=hadoop mode=755"
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-core-1.9.jar dest=/app/spark-2.2.1-bin-hadoop2.9.0/jars  owner=spark group=hadoop mode=755"

启动spark thrift server
ansible thriftserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark221/sbin && ./launch-thriftserver.sh'"
切换软连接
ansible all -i spark.host -mshell -a"rm -f /opt/spark220;ln -s /app/spark-2.2.1-bin-hadoop2.9.0 /opt/spark220;chown -h spark:hadoop /opt/spark220"


