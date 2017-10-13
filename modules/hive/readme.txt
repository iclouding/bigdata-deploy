此项目包括hive的部署包及其部署脚本

cd /data/tools/ansible/modules
//获取代码
git pull
一、创建mysql用户
在bigdata-cmpt-128-25 hive库中添加
用户：hive
密码：hive@whaley
确保 hive库使用latin1 编码，若不是执行：
使用hadoop 用户操作
mysql -uroot -p'moretvsmarTV@608_810'
create database hive;
grant all on hive.* to hive@'%'  IDENTIFIED BY 'hive@whaley';
alter database hive character set latin1;

数据库初始化:
./bin/schematool  -initSchema -dbType mysql
$HIVE_HOME/scripts/metastore/upgrade/mysql

二、在bigdata-cmpt-128-1 上执行命令，创建hive metastore 路径以及修改所有者
    su - hdfs -c "hadoop fs -mkdir -p /user/hive/warehouse && hadoop fs -chown -R hadoop:hadoop /user/hive/warehouse "

二、启动
1.按照hive.host文件中定义的主机进行分发tar包和配置文件
ansible-playbook -i hive.host install_hive.yml

2.在bigdata-cmpt-128-1、bigdata-cmpt-128-13、bigdata-cmpt-128-25执行$HIVE_HOME/bin/hive --service metastore &，启动hive 的 metastore集群
三、验证hive 是否可用
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

四、验证hive ha
    ps -ef|grep HiveServer2|grep -v grep| awk '{print \$2}'|xargs kill -9 ;
    杀死任意2个hive metasote ,执行 查询观察是否可用

#启动hiveserver2
#ansible hiveserver2 -i hive.host -m shell -a "ps -ef|grep HiveServer2|grep -v grep| awk '{print \$2}'|xargs kill -9 ; su - hadoop -c 'nohup /opt/hive/bin/hiveserver2  --hiveconf fs.hdfs.impl.disable.cache=true --hiveconf fs.file.impl.disable.cache=true &' "
ansible-playbook -i hive.host install_hive.yml -t config
ansible hiveserver2 -i hive.host -m shell -a " su - hadoop -c 'nohup /opt/hive/bin/hiveserver2   &' "

#启动HiveMetaStore
ansible-playbook -i hive.host install_hive.yml -t config
ansible hiveserver2 -i hive.host -m shell -a "ps -ef|grep HiveMetaStore|grep -v grep| awk '{print \$2}'|xargs kill -9 ; su - hadoop -c 'nohup /opt/hive/bin/hive --service metastore &' "


#tez安装
ansible all -i hive.host -m shell -a"rm -f /opt/tez/.install"
ansible-playbook -i hive.host install_tez.yml

#tez配置更新
ansible-playbook -i hive.host install_tez.yml -t config

#tomcat安装
ansible tez-ui -i hive.host -m shell -a"rm -f /opt/tomcat/.install"
ansible-playbook -i hive.host install_tomcat.yml
ansible-playbook -i hive.host install_tomcat.yml -t config

#tomcat操作
ansible tez-ui -i hive.host -m shell -a"su - hadoop -c /opt/tomcat/bin/startup.sh"
ansible tez-ui -i hive.host -m shell -a"su - hadoop -c /opt/tomcat/bin/shutdown.sh"

#hplsql操作
ansible all -i hive.host -m shell -a"rm -f /opt/hplsql/.install"
ansible-playbook -i hive.host install_hplsql.yml
ansible-playbook -i hive.host install_hplsql.yml -t config


#hive2.1.1
ansible-playbook -i hive.host install_hive2.1.1.yml -t install
ansible-playbook -i hive.host install_hive2.1.1.yml -t config
ansible-playbook -i hive.host install_hive2.1.1.yml -t link
ansible-playbook -i hive.host install_hive2.1.1.yml -t updatejar
ansible-playbook -i hive.host install_hive2.1.1.yml -t updatejar-hcatalog

ansible all -i hive.host -mcopy -a"src=/data/tools/ansible/modules/hive/config/hive-site.xml dest=/opt/hive/conf  owner=hadoop group=hadoop mode=755"
ansible all -i hive.host -mcopy -a"src=/data/tools/ansible/modules/hive/config/hive-env.sh dest=/opt/hive/conf  owner=hadoop group=hadoop mode=755"
ansible all -i hive.host -mcopy -a"src=/data/tools/ansible/modules/hive/package/hive-exec-2.1.1.jar dest=/opt/hive/lib  owner=hadoop group=hadoop mode=755"
ansible all -i hive.host -mcopy -a"src=/data/tools/ansible/modules/hive/config/hive.sh dest=/opt/hive/bin/hive  owner=hadoop group=hadoop mode=755"



#初次使用需初始化数据库： ./bin/schematool -dbType mysql -initSchema

#启动metastore服务：nohup /app/apache-hive-2.1.1-bin/bin/hive --service metastore -p 9083 &


#slider
ansible-playbook -i hive.host install_slider.yml -t install
ansible-playbook -i hive.host install_slider.yml -t config
ansible-playbook -i hive.host install_slider.yml -t link

#stderr 线上任务经常出现/dev/stderr不能访问的问题,显示创建用户对应的stderr目录来避免该问题
ansible all -i hive.host -m shell -a"mkdir -p /tmp/hadoop/ && touch /tmp/hadoop/stderr && chmod -R 777 /tmp/hadoop/stderr"
ansible all -i hive.host -m shell -a"mkdir -p /tmp/spark/ && touch /tmp/spark/stderr && chmod -R 777 /tmp/spark/stderr"

#
ansible all -i hive.host -mcopy -a"src=/data/tools/ansible/modules/hive/package/hive-serde-2.1.1.jar dest=/opt/hive/lib  owner=hadoop group=hadoop mode=755"
ansible all -i hive.host -mcopy -a"src=/data/tools/ansible/modules/hive/package/hive-exec-2.1.1.jar dest=/opt/hive/lib  owner=hadoop group=hadoop mode=755"




#udf修改操作
自定义udf函数时候，尽量使用jdk内置的方法，不要引用外部包
一、测试
1.上传工程jar到指定的位置。如 /opt/xx.jar
2.进入hive客户端
3.加载jia
add /opt/xx.jar;
4.创建临时函数
create temporary function xx as 'xx.xxx.xx.Class' ;
5.执行sql
select xx('a') from test limit 10;

二、上生产(部分相关人员才可以操作)
1.上传jar 到hdfs 目录上
hadoop fs -rm -r /libs/udf/DataWarehouseUdf-1.0-SNAPSHOT.jar  (先备份一下)
hadoop fs -put  DataWarehouseUdf-1.0-SNAPSHOT.jar /libs/udf/
2.修改/opt/hive/conf/.hiverc,添加创建临时函数
create temporary function xxx..
3.上传.hiverc 到ftp上
fput .hiverc
4.在管理机上分发.hiverc hadoop  manager 上
 cd  /data/tools/ansible/modules/hive/playbook
 ansible all -i hive.host -m shell -a 'cd /opt/hive/conf/; python /data/tscripts/scripts/ftp.py -s get -f .hiverc'
5.修改权限
ansible all -i hive.host -m shell -a 'cd /opt/hive/conf/; chmod 771 .hiverc '
6.重启hiveserver2
ansible hiveserver2 -i hive.host -m shell -a "ps -ef|grep HiveServer2|grep -v grep| awk '{print \$2}'|xargs kill -9 ; nohup /opt/hive/bin/hiveserver2 > /data/logs/hive/hiveserver2.log 2>&1 &'"




