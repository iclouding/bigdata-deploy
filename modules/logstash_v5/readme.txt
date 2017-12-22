此项目包括logstash-5.2.0(kafka的topic切分)的部署包及其部署脚本

以下功能指令均需在/data/tools/ansible/modules/logstash_v5/playbook中执行

现在使用bigdata-appsvr-130-5,bigdata-appsvr-130-6作为kafka分流使用

--安装包分发
ansible-playbook -i logstash.host install_logstash-bin.yml -t install

--配置分发
ansible-playbook -i logstash.host install_logstash-bin.yml -t config

--创建基本topic
ssh bigdata-appsvr-130-1
cd /opt/kafka3
bin/kafka-topics.sh --create --topic helios-pre-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 18
bin/kafka-topics.sh --create --topic helios-processed-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 18
bin/kafka-topics.sh --create --topic medusa-pre-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 48
bin/kafka-topics.sh --create --topic medusa-processed-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 48
bin/kafka-topics.sh --create --topic helios-pre-error-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 18
bin/kafka-topics.sh --create --topic medusa-pre-error-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 18

--生产业务4条启动命名
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash_v5/bin;sh start_logstash.sh kafka_topic_distribute_helios_hot_16.conf'"
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash_v5/bin;sh start_logstash.sh kafka_topic_distribute_helios_status.conf'"
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash_v5/bin;sh start_logstash.sh kafka_topic_distribute_jianianhua.conf'"
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash_v5/bin;sh start_logstash.sh kafka_topic_distribute_medusa_hot.conf'"

#广告业务，暂时停止
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash_v5/bin;sh start_logstash.sh kafka_topic_distribute_ad_turnon_medusa_product.conf'"
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash_v5/bin;sh start_logstash.sh kafka_topic_distribute_ad_vod_whaley_product.conf'"

--停止logsash实例
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash_v5/bin;sh stop_logstash.sh kafka_topic_distribute_ad_turnon_medusa_product.conf'"
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash_v5/bin;sh stop_logstash.sh kafka_topic_distribute_ad_vod_whaley_product.conf'"


--增加cronjob
ansible logstashs -i logstash.host -m cron -a "name='logstash autostart job 1' minute=*/6  user='moretv' job='. /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_helios_hot_16.conf > /dev/null 2>&1'  "
ansible logstashs -i logstash.host -m cron -a "name='logstash autostart job 2' minute=*/6  user='moretv' job='. /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_helios_status.conf > /dev/null 2>&1'  "
ansible logstashs -i logstash.host -m cron -a "name='logstash autostart job 3' minute=#*/6  user='moretv' job='. /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_jianianhua.conf > /dev/null 2>&1'  "
ansible logstashs -i logstash.host -m cron -a "name='logstash autostart job 4' minute=*/6  user='moretv' job='. /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_medusa_hot.conf > /dev/null 2>&1'  "
ansible logstashs -i logstash.host -m cron -a "name='logstash autostart job 5' minute=#*/6  user='moretv' job='. /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_ad_turnon_medusa_product.conf > /dev/null 2>&1'  "
ansible logstashs -i logstash.host -m cron -a "name='logstash autostart job 6' minute=#*/6  user='moretv' job='. /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_ad_vod_whaley_product.conf > /dev/null 2>&1'  "
ansible logstashs -i logstash.host -m cron -a "name='logstash autostart job 7' minute=*/6  user='moretv' job='. /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_helios_player_sdk_startplay.conf > /dev/null 2>&1'  "
ansible logstashs -i logstash.host -m cron -a "name='logstash autostart job 8' minute=*/6  user='moretv' job='. /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_medusa_player_sdk_startplay.conf > /dev/null 2>&1'  "
ansible logstashs -i logstash.host -m cron -a "name='logstash autostart job 9' minute=*/6  user='moretv' job='. /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_player_sdk_startplay_merge.conf > /dev/null 2>&1'  "


--------------------Example to create topic for kylin ansible--------------------
以依据业务创建kafka_topic_distribute_helios_hot_16.conf为例
创建分流到kafka 0.10.1.0的集群
ssh bigdata-appsvr-130-1
su - moretv
1.创建kafka topic
cd /opt/kafka3
bin/kafka-topics.sh --create --topic kylin-hot-play --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 6
2.编写logstash配置文件，kafka_topic_distribute_helios_hot_16.conf
3.编写用来分发的配置项
在logstash-config.yml文件中增加一条item
4.配置分发
cd /data/tools/ansible/modules/logstash_v5/playbook
ansible-playbook -i logstash.host logstash-config.yml -t business_config
5.启动
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash_v5/bin;sh start_logstash.sh kafka_topic_distribute_helios_hot_16.conf'"
6.停止
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash_v5/bin;sh stop_logstash.sh kafka_topic_distribute_helios_hot_16.conf'"




--------------------how to install logstash-filter-prune--------------------
当logstash的filter需要prune插件的时候，安装步骤：
#use root user to install ruby and rubygems
#sudo yum install ruby
#sudo yum install rubygems
#
# use moretv user to install logstash-filter-prune
# /opt/logstash_v5/bin/logstash-plugin install logstash-filter-prune

--------------------other:check kafka log--------------------
ssh bigdata-appsvr-130-1
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic   helios-pre-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic   helios-processed-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic   KYLIN-AD-TURNON-PLAY-MEDUSA-PRODUCT-TOPIC  -bootstrap-server bigdata-appsvr-130-1:9094 | head
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic   KYLIN-AD-TURNON-REQUEST-MEDUSA-PRODUCT-TOPIC  -bootstrap-server bigdata-appsvr-130-1:9094 | head
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic   KYLIN-AD-VOD-PRE-PLAY-PRODUCT-TOPIC  -bootstrap-server bigdata-appsvr-130-1:9094 | head
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic   KYLIN-AD-VOD-PRE-REQUEST-PRODUCT-TOPIC  -bootstrap-server bigdata-appsvr-130-1:9094 | head
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic   medusa-playqos-output-product  -bootstrap-server bigdata-appsvr-130-1:9094 | head
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic   medusa-processed-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head
sh /opt/kafka3/bin/kafka-console-consumer.sh --topic   medusa-pre-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head

ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash_v5/bin;sh start_logstash.sh kafka_topic_distribute_helios_player_sdk_startplay.conf'"


--- 下面的服务是用来做剧集下线使用【62错误码】
   #Ansible: logstash autostart job 7
   */6 * * * * source /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_helios_player_sdk_startplay.conf > /dev/null 2>&1
   #Ansible: logstash autostart job 8
   */6 * * * * source /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_medusa_player_sdk_startplay.conf > /dev/null 2>&1
   #Ansible: logstash autostart job 9
   */6 * * * * source /etc/profile;sh /opt/logstash_v5/bin/start_logstash.sh kafka_topic_distribute_player_sdk_startplay_merge.conf > /dev/null 2>&1


   sh /opt/kafka3/bin/kafka-console-consumer.sh --topic openrs-medusa-player-sdk-startplay  -bootstrap-server bigdata-appsvr-130-1:9094 |head