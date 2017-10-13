#sqoop安装
ansible all -i sqoop.host -m shell -a"rm -f /opt/sqoop/.install"
ansible-playbook -i sqoop.host install_sqoop.yml

#配置更新
ansible-playbook -i sqoop.host install_sqoop.yml -t config
ansible all -i sqoop.host -mcopy -a"src=/data/tools/ansible/modules/sqoop/sqoop1/config/sqoop-env.sh dest=/opt/sqoop/conf  owner=hadoop group=hadoop mode=755"



