此项目包括kylin的部署包及其部署脚本

需要提前配置
KYLIN_HOME=/opt/kylin
KAFKA_HOME=/opt/kafka3

确保hive，hbase，hadoop, kafka的客户端可用

cd /data/tools/ansible/modules/kylin/playbook

ansible-playbook -i kylin.host install_kylin.yml

ansible all -i kylin.host -mshell -a"su - hadoop -c '/opt/kylin/bin/kylin.sh start'"

重启kylin query server
ansible all -i kylin_query.host -mshell -a"su - hadoop -c '. /etc/profile;sh /opt/kylin/bin/kylin_query_server_restart.sh' "


分发配置到查询机器
ansible-playbook -i kylin_query.host install_kylin.yml -t config

添加crontab
ansible all -i kylin.host -m cron -a "name='check kylin job1' minute=*/6  user='hadoop' job='. /etc/profile;sh /opt/kylin/bin/kylin_monitor.sh >/dev/null 2>&1'"

定时重启kylin query server
ansible all -i kylin_query.host -m cron -a "name='restart kylin query server job' hour=3 minute=30 weekday=3,6 user='hadoop' job='. /etc/profile;sh /opt/kylin/bin/kylin_query_server_restart.sh >>/data/logs/kylin/kylin_query_restart.log 2>&1'"