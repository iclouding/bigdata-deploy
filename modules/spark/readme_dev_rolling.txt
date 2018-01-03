
----------------------------------------spark devx滚动升级步骤----------------------------------------

--替换jersey相关jar包[可以提前做]
cd /data/tools/ansible/modules/spark/playbook
ansible all -i dev.host -mshell -a"mkdir /app/spark-2.1.2-bin-hadoop2.9.0/bk ; mv /app/spark-2.1.2-bin-hadoop2.9.0/jars/jersey-client-*.jar /app/spark-2.1.2-bin-hadoop2.9.0/bk "
ansible all -i dev.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-client-1.9.jar dest=/app/spark-2.1.2-bin-hadoop2.9.0/jars  owner=spark group=hadoop mode=755"
ansible all -i dev.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-core-1.9.jar dest=/app/spark-2.1.2-bin-hadoop2.9.0/jars  owner=spark group=hadoop mode=755"

--重启HistoryServer【在正式切换的时候操作】
1.关闭HistoryServer
ansible historyserver -i dev.host -mshell -a"su - spark -c 'cd /opt/spark2/sbin && ./stop-history-server.sh'"
2.切换软连接
ansible all -i dev.host -mcopy -a"rm -f /opt/spark2;ln -s /app/spark-2.1.2-bin-hadoop2.9.0 /opt/spark2;chown -h spark:hadoop /opt/spark2"
3.启动HistoryServer
ansible historyserver -i dev.host -mshell -a"su - spark -c 'cd /opt/spark2/sbin && ./start-history-server.sh'"

