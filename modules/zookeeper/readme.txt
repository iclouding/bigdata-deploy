此项目包括zookeeper相关的部署包及其部署脚本
启动服务
ansible all -i zk_master.host -mshell -a"su - moretv -c 'cd /opt/zookeeper/ && nohup ./bin/zkServer.sh start &'"
查看服务运行情况
ansible all -i zk_master.host -mshell -a"su - moretv -c 'cd /opt/zookeeper/ &&  ./bin/zkServer.sh status &'"


ansible all -i zk_app_test.host -mshell -a"su - moretv -c 'cd /opt/zookeeper1/ && nohup ./bin/zkServer.sh start &'"
ansible all -i zk_app_test.host -mshell -a"su - moretv -c 'cd /opt/zookeeper1/ &&  ./bin/zkServer.sh status &'"