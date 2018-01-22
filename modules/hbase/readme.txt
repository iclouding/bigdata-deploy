此项目包括hbase的部署包及其部署脚本

以下功能指令均需在/data/tools/ansible/modules/hbase/playbook中执行

--安装包分发
ansible-playbook -i hbase.host install_hbase-bin.yml -t install

--配置分发
ansible-playbook -i hbase.host install_hbase-bin.yml -t config

--添加crontab
ansible hmaster -i hbase.host -m cron -a "name='check hbase master ' minute=*/6  user='hadoop' job='sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.master.HMaster master >/dev/null 2>&1'  "
ansible hbase-master-backup -i hbase.host -m cron -a "name='check hbase master ' minute=*/6  user='hadoop' job='sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.master.HMaster master >/dev/null 2>&1'  "
ansible regionserver -i hbase.host -m cron -a "name='check hbase regionserver ' minute=*/2  user='hadoop' job='. /etc/profile;sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.regionserver.HRegionServer regionserver >/dev/null 2>&1'  "



--配置hbase的hdfs目录
以root用户执行,on bigdata-cmpt-128-1 machine
su - hdfs -c  "hadoop fs -mkdir -p /apache-hbase"
su - hdfs -c  "hadoop fs -chown -R hadoop:hadoop /apache-hbase"

--启动hbase[慎用]
ansible hmaster -i hbase.host -mshell -a"su - hadoop -c  'cd /opt/hbase/bin;sh start-hbase.sh'"

--停止hbase[慎用]
ansible hmaster -i hbase.host -mshell -a"su - hadoop -c  'cd /opt/hbase/bin;sh stop-hbase.sh'"

--重启hbase ThriftServer
ansible all -i hbase.host -mcopy -a"src=/data/tools/ansible/modules/hbase/config/etc/hbase/hbase-env.sh dest=/opt/hbase/conf  owner=hadoop group=hadoop mode=755"
ansible all -i hbase.host -mcopy -a"src=/data/tools/ansible/modules/hbase/config/etc/hbase/hbase-site.xml dest=/opt/hbase/conf  owner=hadoop group=hadoop mode=755"
ansible hbase-thriftserver -i hbase.host -m shell -a "ps -ef|grep -i hbase|grep -i thriftserver|grep -v grep| awk '{print \$2}'|xargs kill -9 ; su - hadoop -c '/opt/hbase/bin/hbase-daemon.sh start thrift' "

-----------重启单台habse regionserver-----------
登录到regionserver机器
/opt/hbase/bin/hbase-daemon.sh restart regionserver

-----------加入单台habse regionserver-----------
1. $HBASE_HOME/conf/regionservers 加入新的regionserver
[使用ansible分发，理论上只需要更新Master node到regionservers文件，现在全部更新文件
ansible-playbook -i hbase.host install_hbase-bin.yml -t config]
2. /opt/hbase/bin/hbase-daemon.sh start regionserver



-----------下线单台habse regionserver[慎重]-----------
登陆到需要下线的regionserver,sh /opt/hbase/bin/graceful_stop.sh hostname
hostname替换为机器名称，例如bigdata-cmpt-128-19


------------------------------滚动重启所有hbase------------------------------
1.停止hbase regionserver cronjob监控[防止hbase滚动重启过程中，监控拉起hbase相关服务]
在ansible机器上,hbase/playbook目录，执行
ansible regionserver -i hbase.host -m cron -a "name='check hbase regionserver ' state=absent minute=*/6  user='hadoop' job='. /etc/profile;sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.regionserver.HRegionServer regionserver >/dev/null 2>&1'  "
ansible hmaster -i hbase.host -m cron -a "name='check hbase master ' state=absent minute=*/6  user='hadoop' job='sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.master.HMaster master >/dev/null 2>&1'  "
ansible hbase-master-backup -i hbase.host -m cron -a "name='check hbase master ' state=absent minute=*/6  user='hadoop' job='sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.master.HMaster master >/dev/null 2>&1'  "

-------------
2.开始滚动重启
在hbase-master机器，bigdata-cmpt-128-1，发布滚动重启命令
nohup sh /opt/hbase/bin/rolling-restart.sh > rolling.log 2>&1 &
如果在rolling.log日志里发现"Waiting for /hbase/region-in-transition to empty 3"日志，参考[note1]解决
a.--graceful参数表示迁移rs上的数据[可以用来进行版本的热升级,单纯的配置改动后生效,不需要指定此参数。]
b.--rs-only参数表示只是重启rs
c.--master-only参数表示只是重启master
d.一般不需要手动启动负载均衡
  手动启动负载均衡,在hbase-master机器
  sh /opt/hbase/bin/hbase shell
  运行： balance_switch true
-------------

4.启动hbase cronjob
在ansible机器上,hbase/playbook目录，执行
ansible hmaster -i hbase.host -m cron -a "name='check hbase master ' minute=*/6  user='hadoop' job='sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.master.HMaster master >/dev/null 2>&1'  "
ansible hbase-master-backup -i hbase.host -m cron -a "name='check hbase master ' minute=*/6  user='hadoop' job='sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.master.HMaster master >/dev/null 2>&1'  "
ansible regionserver -i hbase.host -m cron -a "name='check hbase regionserver ' minute=*/6  user='hadoop' job='. /etc/profile;sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.regionserver.HRegionServer regionserver >/dev/null 2>&1'  "
------------------------------滚动重启所有hbase------------------------------end


[note1]
以moretv用户执行命令
/opt/zookeeper1/bin/zkCli.sh  -server bigdata-cmpt-128-1:2181
ls /hbase/region-in-transition
[17514a4bfce382917e93eb7d1582c891, 11aaf64c957167f2535a9e1c288c3cc6, d050d80d3698f26b0f79921a5c908d5a]
当里面没有数值，依次删除文件
delete /hbase/region-in-transition/11aaf64c957167f2535a9e1c288c3cc6