
#安装应用
ansible-playbook -i biserver.host install_cis-bi.yml -t install

#配置下发
ansible-playbook -i biserver.host install_cis-bi.yml -t config

#启动应用
ansible all -i biserver.host -mshell -a"su - moretv -c '/opt/biserver/cis-bi/server/bin/startup.sh'"

#停止应用
ansible all -i biserver.host -mshell -a"su - moretv -c '/opt/biserver/cis-bi/server/bin/shutdown.sh'"

#重启应用
ansible all -i biserver.host -mshell -a"su - moretv -c '/opt/biserver/cis-bi/server/bin/restart.sh'"
