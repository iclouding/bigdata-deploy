此项目包括hbase的部署包及其部署脚本

以下功能指令均需在/data/tools/ansible/modules/hbase/playbook中执行

--安装包分发
ansible-playbook -i hbase_test.host install_hbase-bin_test.yml -t install

--配置分发
ansible-playbook -i hbase_test.host install_hbase-bin_test.yml -t config

--添加crontab
ansible hmaster -i hbase_test.host -m cron -a "name='check hbase master ' minute=*/6  user='hadoop' job='sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.master.HMaster master >/dev/null 2>&1'  "
ansible hbase-master-backup -i hbase_test.host -m cron -a "name='check hbase master ' minute=*/6  user='hadoop' job='sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.master.HMaster master >/dev/null 2>&1'  "
ansible regionserver -i hbase_test.host -m cron -a "name='check hbase regionserver ' minute=*/6  user='hadoop' job='. /etc/profile;sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.regionserver.HRegionServer regionserver >/dev/null 2>&1'  "



--配置hbase的hdfs目录
以root用户执行,on bigdata-cmpt-128-1 machine
su - hdfs -c  "hadoop fs -mkdir -p /apache-hbase"
su - hdfs -c  "hadoop fs -chown -R hadoop:hadoop /apache-hbase"

--启动hbase[慎用]
ansible hmaster -i hbase_test.host -mshell -a"su - hadoop -c  'cd /opt/hbase/bin;sh start-hbase.sh'"

--停止hbase[慎用]
ansible hmaster -i hbase_test.host -mshell -a"su - hadoop -c  'cd /opt/hbase/bin;sh stop-hbase.sh'"

--重启regionserver
ansible regionserver -i hbase_test.host -mshell -a"su - hadoop -c'/opt/hbase/bin/hbase-daemon.sh restart regionserver'"

ansible regionserver -i hbase_test.host -mshell -a"su - hadoop -c'ps -ef|grep regionserver'"

--重启hbase ThriftServer
ansible all -i hbase_test.host -mcopy -a"src=/data/tools/ansible/modules/hbase/config_test/etc/hbase/hbase-env.sh dest=/opt/hbase/conf  owner=hadoop group=hadoop mode=755"
ansible all -i hbase_test.host -mcopy -a"src=/data/tools/ansible/modules/hbase/config/etc/hbase/hbase-site.xml dest=/opt/hbase/conf  owner=hadoop group=hadoop mode=755"
ansible hbase-thriftserver -i hbase_test.host -m shell -a "ps -ef|grep -i hbase|grep -i thriftserver|grep -v grep| awk '{print \$2}'|xargs kill -9 ; su - hadoop -c '/opt/hbase/bin/hbase-daemon.sh start thrift' "

-----------关闭单台habse regionserver-----------
登陆到需要关闭regionserver的机器上,sh /opt/hbase/bin/graceful_stop.sh hostname
hostname替换为机器名称，例如bigdata-cmpt-128-18
nohup sh /opt/hbase/bin/graceful_stop.sh bigdata-cmpt-128-18 > graceful_stop.log 2>&1
bigdata-cmpt-128-18机器上的region会向其他regionserver迁移，迁移完成后自动关闭。

-----------加入单台habse regionserver-----------
1. $HBASE_HOME/conf/regionservers 加入新的regionserver
[使用ansible分发，理论上只需要更新Master node到regionservers文件，现在全部更新文件
ansible-playbook -i hbase_test.host install_hbase-bin_test.yml -t config]
2. /opt/hbase/bin/hbase-daemon.sh start regionserver


-----------滚动重启所有hbase regionserver步骤[慎用,下面操作是关闭所有region server
]-----------
1.停止hbase regionserver cronjob监控,防止hbase滚动重启过程中，监控拉起hbase regionserver
在ansible机器上,hbase/playbook目录，执行
  ansible regionserver -i hbase_test.host -m cron -a "name='check hbase regionserver ' minute=#*/6  user='hadoop' job='. /etc/profile;sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.regionserver.HRegionServer regionserver >/dev/null 2>&1'  "

2.在hbase-master机器，bigdata-cmpt-128-1，发布滚动重启命令
nohup sh /opt/hbase/bin/rolling-restart.sh --rs-only  --graceful > rolling.log 2>&1 &
3.手动启动负载均衡,在hbase-master机器，sh /opt/hbase/bin/hbase shell
运行： balance_switch true
4.启动hbase regionserver cronjob
在ansible机器上,hbase/playbook目录，执行
  ansible regionserver -i hbase_test.host -m cron -a "name='check hbase regionserver ' minute=*/6  user='hadoop' job='. /etc/profile;sh /opt/hbase/conf/monitor_hbase.sh org.apache.hadoop.hbase.regionserver.HRegionServer regionserver >/dev/null 2>&1'  "




/opt/hbase/bin/hbase-daemon.sh start   regionserver
/opt/hbase/bin/hbase-daemon.sh restart regionserver
ansible regionserver -i hbase_test.host -mshell -a"su - hadoop -c'/opt/hbase/bin/hbase-daemon.sh start regionserver'"
ansible regionserver -i hbase_test.host -mshell -a"su - hadoop -c'/opt/hbase/bin/hbase-daemon.sh stop regionserver'"
ansible hmaster             -i hbase_test.host -mshell -a"su - hadoop -c'/opt/hbase/bin/hbase-daemon.sh start master'"
ansible hbase-master-backup -i hbase_test.host -mshell -a"su - hadoop -c'/opt/hbase/bin/hbase-daemon.sh start master'"


ansible hmaster             -i hbase_test.host -mshell -a"su - hadoop -c'/opt/hbase/bin/hbase-daemon.sh stop master'"
ansible hbase-master-backup -i hbase_test.host -mshell -a"su - hadoop -c'/opt/hbase/bin/hbase-daemon.sh stop master'"


ansible regionserver -i hbase_test.host -mshell -a"su - hadoop -c'jps'"


ansible regionserver -i hbase_test.host -mshell -a"su - hadoop -c'jps'"
ansible hmaster -i hbase_test.host -mshell -a"su - hadoop -c'jps'"
ansible hbase-master-backup -i hbase_test.host -mshell -a"su - hadoop -c'jps'"




------------测试环境配置prometheus------------
ansible all -i hbase_test.host -mcopy -a"src=/data/tools/ansible/modules/hbase/config_test/etc/hbase/hbase-env.sh dest=/opt/hbase/conf  owner=hadoop group=hadoop mode=755"
ansible all -i hbase_test.host -mshell -a"su - hadoop -c' mkdir -p /opt/hbase/prometheus '"
ansible all -i hbase_test.host -mcopy -a"src=/data/tools/ansible/modules/hbase/config_test/etc/hbase/jmx_prometheus_javaagent-0.1.0.jar dest=/opt/hbase/prometheus  owner=hadoop group=hadoop mode=755"
ansible all -i hbase_test.host -mcopy -a"src=/data/tools/ansible/modules/hbase/config_test/etc/hbase/hbase_jmx_config.yaml dest=/opt/hbase/prometheus  owner=hadoop group=hadoop mode=755"
ansible regionserver -i hbase_test.host -mshell -a"su - hadoop -c'/opt/hbase/bin/hbase-daemon.sh restart regionserver'"
ansible hmaster      -i hbase_test.host -mshell -a"su - hadoop -c'/opt/hbase/bin/hbase-daemon.sh restart hmaster'"

ansible hbase-master-backup -i hbase_test.host -mshell -a"su - hadoop -c'/opt/hbase/bin/hbase-daemon.sh stop master'"
ansible hbase-master-backup -i hbase_test.host -mshell -a"su - hadoop -c'/opt/hbase/bin/hbase-daemon.sh start master'"
