测试kafka，杀掉所有kafka进程【kafka1,kafka4等】
ansible all -i kafka_test.host -mshell -a"su - moretv -c 'cd /opt/kafka1/ &&  ./bin/kafka-server-stop.sh '"

查看kafka进程
ansible all -i kafka_test.host -mshell -a"su - moretv -c 'ps -ef|grep kafka '"


测试环境，如果使用，需要重新部署。
--------------------------------------------安装kafka3-----------------------------------------------------------------------
---------------kafka3---------------
--定制启动停止脚本分发
ansible-playbook -i kafka_test.host install_kafka_bin_3_test.yml
