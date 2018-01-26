ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/config_test/spark2.2.0/spark-thrift-sparkconf.conf dest=/opt/spark220/conf owner=spark group=hadoop mode=755"
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/config_test/spark2.2.0/launch-thriftserver.sh dest=/opt/spark220/sbin owner=spark group=hadoop mode=755"
ansible thriftserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark220/sbin && ./launch-thriftserver.sh'"
ansible thriftserver -i spark.host -mshell -a"su - spark -c 'cd /opt/spark220/sbin && ./stop-thriftserver.sh'"


ansible all -i spark.host -mshell -a"su - spark -c 'rm  -r /opt/spark220/config'"


--替换jersey相关jar包
ansible all -i spark.host -mshell -a"mkdir /opt/spark220/bk ; mv /opt/spark220/jars/jersey-client-*.jar /opt/spark220/bk "
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-client-1.9.jar dest=/opt/spark220/jars  owner=spark group=hadoop mode=755"
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/package/jersey-core-1.9.jar dest=/opt/spark220/jars  owner=spark group=hadoop mode=755"
ansible all -i spark.host -mcopy -a"src=/data/tools/ansible/modules/spark/config_test/spark2.2.0/hive-site.xml dest=/opt/spark220/conf owner=spark group=hadoop mode=755"

