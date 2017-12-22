
--安装包分发
ansible-playbook -i spark.host install_spark-2.1.0_hadoop27.yml -t install

--创建spark event log目录：
ansible historyserver -i spark.host -mshell -a"su - hdfs -c 'hadoop fs -mkdir -p /spark-log/spark-events'"
ansible historyserver -i spark.host -mshell -a"su - hdfs -c 'hadoop fs -chown -R spark:hadoop /spark-log'"

--启动HistoryServer
ansible historyserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark2/sbin && ./start-history-server.sh'"

