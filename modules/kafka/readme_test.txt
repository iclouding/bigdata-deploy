测试kafka，杀掉所有kafka进程【kafka1,kafka4等】
ansible all -i kafka_test.host -mshell -a"su - moretv -c 'cd /opt/kafka1/ &&  ./bin/kafka-server-stop.sh '"

查看kafka进程
ansible all -i kafka_test.host -mshell -a"su - moretv -c 'ps -ef|grep kafka '"


测试环境，如果使用，需要重新部署。
--------------------------------------------安装kafka3-----------------------------------------------------------------------
---------------kafka3---------------
--定制启动停止脚本分发
ansible-playbook -i kafka_test.host install_kafka_bin_3_test.yml
ansible all -i kafka_test.host -mcopy -a"src=/data/tools/ansible/modules/kafka/config/kafka3_test/kafka-run-class.sh dest=/opt/kafka3/bin   owner=moretv group=moretv mode=755"


-----启动、停止kafka3系列
ansible all -i kafka_test.host -mshell -a"su - moretv -c 'cd /opt/kafka3 &&  ./bin/kafka-server-stop.sh '"
ansible all -i kafka_test.host -mshell -a"su - moretv -c 'cd /opt/kafka3 &&  ./bin/kafka-server-start.sh -daemon ./config/server.properties '"


ansible all -i kafka_test.host -mshell -a"su - moretv -c 'jps '"
