ncftpput -ubigdata -p'whaley!90365' 10.255.130.6 bigdata/ /home/moretv/filebeat-6.1.1-linux-x86_64.tar.gz


--安装包分发
ansible-playbook -i filebeat.host filebeat-ansible.yml -t install

--业务配置分发
ansible-playbook -i filebeat.host filebeat-ansible.yml -t config_for_apps

--启动filebeat实例
ansible apps -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat/bin;sh start_filebeat.sh app_kafka.yml'"

--停止filebeat实例
ansible apps -i filebeat.host -mshell -a"su - moretv -c  'cd /opt/filebeat/bin;sh stop_filebeat.sh app_kafka.yml'"

--检查filebeat实例
ansible apps -i filebeat.host -mshell -a"su - moretv -c  'ps -ef|grep app_kafka.yml'"

--临时脚本发布
ansible apps -i filebeat.host -mcopy -a"src=/data/tools/ansible/modules/filebeat/config/app_kafka.yml dest=/opt/filebeat/conf owner=moretv group=moretv mode=755"
ansible all -i filebeat.host -mcopy -a"src=/data/tools/ansible/modules/filebeat/config/start_filebeat.sh dest=/opt/filebeat/bin owner=moretv group=moretv mode=755"
ansible all -i filebeat.host -mcopy -a"src=/data/tools/ansible/modules/filebeat/config/stop_filebeat.sh dest=/opt/filebeat/bin owner=moretv group=moretv mode=755"
