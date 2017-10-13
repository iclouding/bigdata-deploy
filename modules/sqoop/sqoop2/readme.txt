#sqoop安装
ansible sqoop2-server -i sqoop.host -m shell -a"rm -f /opt/sqoop2/.install"
ansible-playbook -i sqoop.host install_sqoop.yml

#配置更新
ansible-playbook -i sqoop.host install_sqoop.yml -t config
ansible sqoop2-server -i sqoop.host -mcopy -a"src=/data/tools/ansible/modules/sqoop/sqoop2/config/sqoop-env.sh dest=/opt/sqoop/conf  owner=hadoop group=hadoop mode=755"

#sqoop启动&停止
ansible sqoop2-server -i sqoop.host -m shell -a"su - hadoop -c '/opt/sqoop2/bin/sqoop2-server start'"
ansible sqoop2-server -i sqoop.host -m shell -a"su - hadoop -c '/opt/sqoop2/bin/sqoop2-server stop'"

