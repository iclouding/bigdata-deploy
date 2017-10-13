cd /data/tools/ansible/modules/azkaban/playbook
azkaban web server 安装
ansible-playbook -i azkaban_web.host  install_azkaban_web.yml

azkaban executor server 安装
ansible-playbook -i azkaban_server.host  install_azkaban_server.yml

在bigdata-appsvr-130-7 ,azkaban 数据库中executors表，插入下面数据
insert into executors(host,port,active) values("bigdata-appsvr-130-1",20290,1);
insert into executors(host,port,active) values("bigdata-appsvr-130-2",20290,1);
insert into executors(host,port,active) values("bigdata-appsvr-130-3",20290,1);
insert into executors(host,port,active) values("bigdata-appsvr-130-4",20290,1);
insert into executors(host,port,active) values("bigdata-appsvr-130-5",20290,1);
insert into executors(host,port,active) values("bigdata-appsvr-130-6",20290,1);


针对azkaban webserver
bigdata-appsvr-130-7
cd /opt/azkaban
启动
sh bin/azkaban-web-start.sh
关闭
sh bin/azkaban-web-shutdown.sh


针对azkaban executor server
bigdata-appsvr-130-7
cd /opt/azkaban
启动
sh bin/azkaban-executor-start.sh
关闭
sh bin/azkaban-executor-shutdown.sh



在curl.xml中需要解析json文件，使用jq解析
wget http://stedolan.github.io/jq/download/linux64/jq

chmod +x jq
cp jq /usr/bin

//获取sessionid
curl -k -X POST --data "action=login&username=azkaban&password=azkaban"  https://bigdata-appsvr-130-7:20280

//创建一个project
curl -k -X POST --data "session.id=e2936e6a-1ce6-45e0-a9e5-99551f3e1e9e&name=aaaa&description=11" https://bigdata-appsvr-130-7:20280/manager?action=create

ansible all -i azkaban_server.host -mshell -a "cd /opt/azkaban/conf;chown root execute-as-user;chmod 6050 execute-as-user"

//kill  exec server
ansible all -i azkaban_server.host -mshell -a "su - hadoop -c 'cd /opt/azkaban;sh bin/azkaban-executor-shutdown.sh'"

//kill web server
ansible all -i azkaban_web.host -mshell -a "su - hadoop -c 'cd /opt/azkaban;sh bin/azkaban-web-shutdown.sh'"


//启动


//设置Execute-As-User，用于代理
ansible all -i azkaban_server.host -mshell -a "cd /opt/azkaban/azkaban-exec-server-3.0/conf;chown root execute-as-user"

ansible all -i azkaban_server.host -mshell -a "cd /opt/azkaban/azkaban-exec-server-3.0/conf;chmod 6050 execute-as-user"

//数据库单点宕机
1.启动冷备数据，在bigdata-appsvr-130-6上创建上azkaban数据库
2.使用hadoop 用户，登录bigdata-appsvr-130-6
cd /opt/azkaban/azkaban-web-server-3.0;sh bin/azkaban-web-start.sh
3.给bigdata-appsvr-130-6 上azkaban 数据库