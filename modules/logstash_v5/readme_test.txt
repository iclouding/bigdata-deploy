此项目包括logstash-5.2.0(kafka的topic切分)的部署包及其部署脚本

以下功能指令均需在/data/tools/ansible/modules/logstash_v5/playbook中执行

--安装包分发
ansible-playbook -i logstash_test.host install_logstash-bin.yml -t install

--基础配置分发
ansible-playbook -i logstash_test.host install_logstash-bin.yml -t config


bootstrap_servers => "bigdata-appsvr-130-1:9094,bigdata-appsvr-130-2:9094,bigdata-appsvr-130-3:9094,bigdata-appsvr-130-4:9094,bigdata-appsvr-130-5:9094,bigdata-appsvr-130-6:9094"

cd /opt/kafka3
bin/kafka-topics.sh --create --topic openrs-helios-player-sdk-startplay-test --zookeeper bigtest-appsvr-129-1:2183 --replication-factor 2 --partition 18

sh /opt/kafka3/bin/kafka-console-consumer.sh --topic openrs-helios-player-sdk-startplay-test -bootstrap-server bigtest-appsvr-129-1:9094 | head

