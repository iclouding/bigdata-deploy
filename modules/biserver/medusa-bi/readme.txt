
#安装应用
ansible-playbook -i biserver.host install_medusa-bi.yml -t install

#配置下发
ansible-playbook -i biserver.host install_medusa-bi.yml -t config

#启动应用
ansible all -i biserver.host -mshell -a"su - moretv -c '/opt/biserver/medusa-bi/server/server-1.0.0/bin/startup.sh'"

#停止应用
ansible all -i biserver.host -mshell -a"su - moretv -c '/opt/biserver/medusa-bi/server/server-1.0.0/bin/shutdown.sh'"

#重启应用
ansible all -i biserver.host -mshell -a"su - moretv -c '/opt/biserver/medusa-bi/server/server-1.0.0/bin/restart.sh'"
