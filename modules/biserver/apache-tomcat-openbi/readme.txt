
#安装应用
ansible-playbook -i biserver.host install_apache-tomcat-openbi.yml -t install

#配置下发
ansible-playbook -i biserver.host install_apache-tomcat-openbi.yml -t config

#启动应用
ansible all -i biserver.host -mshell -a"su - moretv -c '/opt/biserver/apache-tomcat-openbi/bin/startup.sh'"


