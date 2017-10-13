此项目包括elasticsearch的部署包及其部署脚本

cd /data/tools/ansible/modules/elasticsearch/playbook

ansible-playbook -i es.host install_es.yml

ansible all -i es.host -mshell -a"su - moretv -c '/opt/elasticsearch/bin/start.sh'"

ansible all -i es.host -mshell -a"su - moretv -c '/opt/elasticsearch/bin/plugin install mobz/elasticsearch-head'"

安装delete-by-query插件，安装后需要重启：
ansible all -i es.host -mshell -a"su - moretv -c '/opt/elasticsearch/bin/plugin install delete-by-query'"
