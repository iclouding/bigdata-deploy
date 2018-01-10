此项目包括logstash-5.2.0(kafka的topic切分)的部署包及其部署脚本

以下功能指令均需在/data/tools/ansible/modules/logstash_v5/playbook中执行

--安装包分发
ansible-playbook -i logstash_test.host install_logstash-bin.yml -t install

--基础配置分发
ansible-playbook -i logstash_test.host install_logstash-bin.yml -t config
