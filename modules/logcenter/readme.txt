此项目包括logcenter的部署包及其部署脚本

--安装包分发
ansible-playbook -i logcenter.host install_logcenter.yml -t install

--配置分发
ansible-playbook -i logcenter.host install_logcenter.yml -t config

--手动执行logcenter相关指令
ansible all -i logcenter.host -mshell -a"su - moretv -c'sh /opt/logcenter1/bin/startup.sh' "
ansible all -i logcenter.host -mshell -a"su - moretv -c'sh /opt/logcenter1/bin/restart.sh' "
ansible all -i logcenter.host -mshell -a"su - moretv -c'sh /opt/logcenter1/bin/shutdown.sh' "
ansible all -i logcenter.host -mshell -a"ps -ef|grep logcenter "
ansible all -i logcenter.host -mshell -a"netstat -anp|grep 20230 "
ansible all -i logcenter.host -mshell -a"lsof -i:20230"