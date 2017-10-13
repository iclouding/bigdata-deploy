测试环境部署步骤

cd /data/tools/ansible/modules
//获取代码
git pull

一、创建mysql用户
在bigtest-cmpt-129-20 hive库中添加
用户：hive
密码：hive@whaley
确保 hive库使用latin1 编码，若不是执行：
使用hadoop 用户操作
mysql -uroot -p'moretvsmarTV@608_810'
create database hive;
grant all on hive.* to hive@'%'  IDENTIFIED BY 'hive@whaley';
alter database hive character set latin1;


二、hdfs初始化
在bigdata-cmpt-129-20 上执行命令，创建hive metastore 路径以及修改所有者
su - hdfs -c "hadoop fs -mkdir -p /user/hive/warehouse && hadoop fs -chown -R hadoop:hadoop /user/hive/warehouse "

三、分发hive
1.按照hive.host文件中定义的主机进行分发tar包和配置文件
cd playbook_test
ansible-playbook -i hive.host install_hive211.yml

四、 数据库初始化:
./bin/schematool  -initSchema -dbType mysql
$HIVE_HOME/scripts/metastore/upgrade/mysql


五、启动hiveserver2
ansible hiveserver2 -i hive.host -m shell -a " su - hadoop -c 'nohup /opt/hive/bin/hiveserver2  > /data/logs/hive/hiveserver2.log 2>&1 &' "

六、启动HiveMetaStore
ansible hiveserver2 -i hive.host -m shell -a "su - hadoop -c 'nohup /opt/hive/bin/hive --service metastore > /data/logs/hive/hivemetastore.log &' "


八、配置phoenix和hbase的lib

九、tez
#tomcat安装
ansible tez-ui -i hive.host -m shell -a"rm -f /opt/tomcat/.install"
ansible-playbook -i hive.host install_tomcat.yml
#ansible-playbook -i hive.host install_tomcat.yml -t config


#tez安装
ansible all -i hive.host -m shell -a"rm -f /opt/tez/.install"
ansible-playbook -i hive.host install_tez.yml

#tez配置更新
#ansible-playbook -i hive.host install_tez.yml -t config

#tomcat操作
ansible tez-ui -i hive.host -m shell -a"su - hadoop -c /opt/tomcat/bin/startup.sh"
ansible tez-ui -i hive.host -m shell -a"su - hadoop -c /opt/tomcat/bin/shutdown.sh"

九、hplsql操作
#先配置apptest-appsvr-192-6上指到hiveserver2的ngnix

ansible all -i hive.host -m shell -a"rm -f /opt/hplsql/.install"
ansible-playbook -i hive.host install_hplsql.yml
ansible-playbook -i hive.host install_hplsql.yml -t config

十、
#slider
ansible-playbook -i hive.host install_slider.yml -t install
ansible-playbook -i hive.host install_slider.yml -t config
ansible-playbook -i hive.host install_slider.yml -t link

#stderr 线上任务经常出现/dev/stderr不能访问的问题,显示创建用户对应的stderr目录来避免该问题
ansible all -i hive.host -m shell -a"mkdir -p /tmp/hadoop/ && touch /tmp/hadoop/stderr && chmod -R 777 /tmp/hadoop/stderr"
ansible all -i hive.host -m shell -a"mkdir -p /tmp/spark/ && touch /tmp/spark/stderr && chmod -R 777 /tmp/spark/stderr"




十一、验证hive 是否可用
   在bigdata-cmpt-128-1、bigdata-cmpt-128-13、bigdata-cmpt-128-25任意一台机器上启动hiveserver2，命令hive --service hiveserver2 &
   通过hive命令进入命令行，建表测试
    //1.创建测试文件
    vi user.txt
    zhangsan    20
    lisi    30
    //2.上传测试文件
    hadoop fs -put user.txt /test/
    //3.创建表
    create table test(name string,age int) row format delimited fields terminated by '\t' ;
    //4.加载测试文件到表中
    load data  inpath '/test/user.txt' overwrite into table test;
    //5.查询
    select * from test;

十二、验证hive ha
    ps -ef|grep HiveServer2|grep -v grep| awk '{print \$2}'|xargs kill -9 ;
    杀死任意2个hive metasote ,执行 查询观察是否可用







py -a"src=/data/tools/ansible/modules/hive/config/hive.sh dest=/opt/hive/bin/hive  owner=hadoop group=hadoop mode=755"



#初次使用需初始化数据库： ./bin/schematool -dbType mysql -initSchema

#启动metastore服务：nohup /app/apache-hive-2.1.1-bin/bin/hive --service metastore -p 9083 &









