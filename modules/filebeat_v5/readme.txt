filebeat-5.2.0版本在filebeat-1.3.1上修复了大量bug，提供了许多新特性，例如直接从文件到kafka的插件。
在配置项上做了大量调整，优化了文件句柄的使用效率，对registry文件的清理以及inode重用问题的尽量避免做了大量改进。

此项目目的除了升级filebeat本身，还有使用filebeat的kafka插件，省略了logstash这一步骤。
forest处理kafka中的数据，需要从helios-pre-log，medusa-pre-log的topic纪录中解析json字符串，
从中获得message的value即为原始日志。

logstash 5.2.0 kafka input plugin need kafka 0.10.0.x version,so filebeat put record to kafka 0.10.0.x version.
In pro env,really kafka version is 0.10.1.0,I need to verify if it work.

此项目包括filebeat的部署包及其部署脚本
以下功能指令均需在/data/tools/ansible/modules/filebeat_v5/playbook中执行

cd /data/tools/ansible/modules/filebeat_v5/playbook
--安装包分发
ansible-playbook -i filebeat.host install_filebeat-bin.yml -t install

--配置分发
ansible-playbook -i filebeat.host install_filebeat-bin.yml -t config
ansible-playbook -i filebeat.host install_filebeat-bin.yml -t config_for_nginx

--启动 helios raw filebeat(logcenter)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh start_filebeat_helios_raw_log.sh'"

--启动 medusa raw filebeat(logcenter)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh start_filebeat_medusa_raw_log.sh'"

--停止 helios raw filebeat(logcenter)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh stop_filebeat_helios_raw_log.sh'"

--停止 medusa raw filebeat(logcenter)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh stop_filebeat_medusa_raw_log.sh'"

--重启 helios raw filebeat(logcenter)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh restart_filebeat_helios_raw_log.sh'"

--重启 medusa raw filebeat(logcenter)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh restart_filebeat_medusa_raw_log.sh'"

--检查 helios raw filebeat(logcenter)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh check_filebeat_helios_raw_log.sh'"

--检查 medusa raw filebeat(logcenter)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh check_filebeat_medusa_raw_log.sh'"


--增加cronjob(logcenter)
ansible filebeats -i filebeat.host -m cron -a "name='filebeat autostart job 1' minute=*/6  user='moretv' job='. /etc/profile;sh /opt/filebeat_v5/start_filebeat_medusa_raw_log.sh >/dev/null 2>&1'"
ansible filebeats -i filebeat.host -m cron -a "name='filebeat autostart job 2' minute=#*/6  user='moretv' job='. /etc/profile;sh /opt/filebeat_v5/start_filebeat_helios_raw_log.sh >/dev/null 2>&1'"

--查看cronjob
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'crontab -l'"


--------------------other:check kafka log--------------------
ssh bigdata-appsvr-130-1
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic medusa-pre-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic medusa-processed-log  -bootstrap-server bigdata-appsvr-130-1:9094| head
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic helios-pre-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic helios-processed-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head

#启动默认appId的nginx日志的filebeat
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c 'cd /opt/filebeat_v5 && bin/startFilebeat.sh filebeat_log-raw-boikgpokn78sb95k00000000.yml'"

#启动medusa产品线nginx日志的filebeat
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c 'cd /opt/filebeat_v5 && bin/startFilebeat.sh filebeat_log-raw-boikgpokn78sb95ktmsc1bnk.yml'"

#启动whaleytv产品线nginx日志的filebeat
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c 'cd /opt/filebeat_v5 && bin/startFilebeat.sh filebeat_log-raw-boikgpokn78sb95kjhfrendo.yml'"

#启动whaleyvr产品线nginx日志的filebeat
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c 'cd /opt/filebeat_v5 && bin/startFilebeat.sh filebeat_log-raw-boikgpokn78sb95kbqei6cc9.yml'"

#启动eagle产品线nginx日志的filebeat
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c 'cd /opt/filebeat_v5 && bin/startFilebeat.sh filebeat_log-raw-boikgpokn78sb95k7id7n8eb.yml'"

#启动orca产品线nginx日志的filebeat
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c 'cd /opt/filebeat_v5 && bin/startFilebeat.sh filebeat_log-raw-boikgpokn78sb95kicggqhbk.yml'"

#启动crawler产品线nginx日志的filebeat，暂不启用
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c 'cd /opt/filebeat_v5 && bin/startFilebeat.sh filebeat_log-raw-boikgpokn78sb95kkls3bhmt.yml'"

#启动mobilehelper产品线nginx日志的filebeat，暂不启用
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c 'cd /opt/filebeat_v5 && bin/startFilebeat.sh filebeat_log-raw-boikgpokn78sb95kjtihcg26.yml'"



--------------------filebeat直接读取nginx写日志--------------------
#监控电视猫main3x的nginx日志的kafka topic
cd /opt/kafka3;
bin/kafka-topics.sh --create --topic log-raw-boikgpokn78sb95ktmsc1bnkechpgj9l --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 48

#监控电视主程序的nginx日志的kafka topic
cd /opt/kafka3;
bin/kafka-topics.sh --create --topic log-raw-boikgpokn78sb95kjhfrendo8dc5mlsr --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 48


--启动 helios raw filebeat(nginx)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh start_filebeat_nginx_whaleytv_main.sh'"

--启动 medusa raw filebeat(nginx)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh start_filebeat_nginx_medusa_3x.sh'"

--停止 helios raw filebeat(nginx)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh stop_filebeat_nginx_whaleytv_main.sh'"

--停止 medusa raw filebeat(nginx)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat_v5;sh stop_filebeat_nginx_medusa_3x.sh'"

--检查电视主程序的nginx日志的filebeat(nginx)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'ps -ef|grep filebeat_nginx_whaleytv_main.yml|grep -v grep|wc -l'"

--检查电视猫main3x的nginx日志的filebeat(nginx)
ansible filebeats -i filebeat.host -mshell -a"su - moretv -c  'ps -ef|grep filebeat_nginx_medusa_3x.yml|grep -v grep|wc -l'"


-------------------filebeat分发给云主机的模版机器-------------------
cd /data/tools/ansible/modules/filebeat_v5/playbook
--安装包分发
ansible-playbook -i filebeat_template.host install_filebeat-bin.yml -t install

--配置分发
ansible-playbook -i filebeat_template.host install_filebeat-bin.yml -t config_for_nginx

--cronjob分发
ansible filebeats -i filebeat_template.host -m cron -a "name='filebeat nginx autostart job 1' minute=*/6  user='moretv' job='. /etc/profile;sh /opt/filebeat_v5/start_filebeat_nginx_medusa_3x.sh >/dev/null 2>&1'"
ansible filebeats -i filebeat_template.host -m cron -a "name='filebeat nginx autostart job 2' minute=*/6  user='moretv' job='. /etc/profile;sh /opt/filebeat_v5/start_filebeat_nginx_whaleytv_main.sh >/dev/null 2>&1'"

--查看进程状态[filebeat_template.host为最新云主机配置]
ansible filebeats -i filebeat_template.host -mshell -a"su - moretv -c  'ps -ef|grep filebeat_nginx_whaleytv_main.yml|grep -v grep|wc -l'"
ansible filebeats -i filebeat_template.host -mshell -a"su - moretv -c  'ps -ef|grep filebeat_nginx_whaleytv_main.yml'"
