
----------------------------------------spark安装步骤----------------------------------------
--替换jersey相关jar包
cd /data/tools/ansible/modules/spark/playbook
ansible all -i dev.host -mshell -a"mkdir /opt/spark2/bk ; mv /opt/spark2/jars/jersey-client-*.jar /opt/spark2/bk "
ansible all -i dev.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-client-1.9.jar dest=/opt/spark2/jars  owner=spark group=hadoop mode=755"
ansible all -i dev.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-core-1.9.jar dest=/opt/spark2/jars  owner=spark group=hadoop mode=755"

--创建spark event log目录：
ansible historyserver -i dev.host -mshell -a"su - hdfs -c 'hadoop fs -mkdir -p /spark-log/spark-events'"
ansible historyserver -i dev.host -mshell -a"su - hdfs -c 'hadoop fs -chown -R spark:hadoop /spark-log'"

--启动HistoryServer
ansible historyserver -i dev.host -mshell -a"su - spark -c 'cd /opt/spark2/sbin && ./start-history-server.sh'"

