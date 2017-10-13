
#安装应用
ansible-playbook -i biserver.host install_happy-kids-english.yml -t install

#配置下发
ansible-playbook -i biserver.host install_happy-kids-english.yml -t config

#启动应用
ansible all -i biserver.host -mshell -a"su - moretv -c '/opt/biserver/happy-kids-english/bin/startup.sh'"

#停止应用
ansible all -i biserver.host -mshell -a"su - moretv -c '/opt/biserver/happy-kids-english/bin/shutdown.sh'"

#重启应用
ansible all -i biserver.host -mshell -a"su - moretv -c '/opt/biserver/happy-kids-english/bin/restart.sh'"
