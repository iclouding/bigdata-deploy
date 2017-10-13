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
create database hive12;
grant all on hive12.* to hive@'%'  IDENTIFIED BY 'hive@whaley';
alter database hive12 character set latin1;

二、hdfs初始化
在bigdata-cmpt-129-20 上执行命令，创建hive metastore 路径以及修改所有者
su - hdfs -c "hadoop fs -mkdir -p /user/hive/warehouse12 && hadoop fs -chown -R hadoop:hadoop /user/hive/warehouse12 "

三、分发hive
1.按照hive.host文件中定义的主机进行分发tar包和配置文件
cd playbook_test12
ansible-playbook -i hive12.host install_hive12.yml

四、 初次使用需初始化数据库:
./bin/schematool  -initSchema -dbType mysql
$HIVE_HOME/scripts/metastore/upgrade/mysql

五、启动HiveMetaStore
替换jersey
ansible-playbook -i hive12.host -m shell -a "su - hadoop -c 'nohup /opt/hive12/bin/hive --service metastore > /data/logs/hive12/hivemetastore.log &' "


已暂停测试服务器hive-1.2.1 metastore server运行，恢复/etc/profile环境变量配置。


