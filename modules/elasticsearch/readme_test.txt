此项目包括elasticsearch的部署包及其部署脚本

cd /data/tools/ansible/modules/elasticsearch/playbook_test

ansible-playbook -i es6.host install_es6.yml -t install
ansible-playbook -i es6.host install_es6.yml -t config


--linux系统配置
ansible all -i es6.host -mshell -a" echo 'vm.max_map_count=262144' >> /etc/sysctl.conf "
ansible all -i es6.host -mshell -a" sysctl -w vm.max_map_count=262144 "


--启动
ansible all -i es6.host -mshell -a"su - moretv -c '/opt/elasticsearch/bin/elasticsearch -d'"

ansible all -i es6.host -mshell -a"su - moretv -c '/opt/elasticsearch/bin/plugin install mobz/elasticsearch-head'"
安装delete-by-query插件，安装后需要重启：
ansible all -i es6.host -mshell -a"su - moretv -c '/opt/elasticsearch/bin/plugin install delete-by-query'"



--检查
ansible all -i es6.host -mshell -a"su - moretv -c 'jps'"
ansible all -i es6.host -mshell -a" cat /etc/sysctl.conf |grep max_map_count"
ansible all -i es6.host -mshell -a" sysctl vm.max_map_count "

--页面
http://bigtest-cmpt-129-202:9200/





问题：
[1]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
参考：
https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html