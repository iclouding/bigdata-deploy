ncftpput -ubigdata -p'whaley!90365' 10.255.130.6 bigdata/ /home/moretv/logstash-6.1.1.tar.gz

cd /data/tools/ansible/modules/logstash/playbook

--安装包分发
ansible-playbook -i logstash.host logstash-ansible.yml -t install

--业务配置分发
ansible-playbook -i logstash.host logstash-ansible.yml -t config

--启动业务logstash
-监控tpc端口logstash
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash/bin;sh start_logstash.sh read_port_info.conf'"

-接受filebeat发送的数据
ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'cd /opt/logstash/bin;sh start_logstash.sh read_from_filebeat.conf'"


ansible logstashs -i logstash.host -mshell -a"su - moretv -c  'ps -ef|grep read_from_filebeat.conf'"


ansible logstashs -i logstash.host -mcopy -a"src=/data/tools/ansible/modules/logstash/config/logstash.yml dest=/opt/logstash/config owner=moretv group=moretv mode=755"

ansible logstashs -i logstash.host -mshell -a"chown -R moretv:moretv /data/apps/logstash"

nohup ./logstash -f ../config/read_port_info.conf --config.reload.automatic --path.data /data/apps/logstash/read_port_info.conf >a.log 2>&1 &

