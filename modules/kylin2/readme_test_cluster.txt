此项目包括kylin的部署包及其部署脚本

需要提前配置 (~/.bash_profile)

KYLIN_HOME=/opt/kylin
KAFKA_HOME=/opt/kafka3

确保hive，hbase，hadoop, kafka的客户端可用

cd /data/tools/ansible/modules/kylin/playbook

ansible-playbook -i kylin_test.host install_kylin_test.yml

ansible all -i kylin_test.host -mshell -a"su - hadoop -c '/opt/kylin/bin/kylin.sh start'"

 
