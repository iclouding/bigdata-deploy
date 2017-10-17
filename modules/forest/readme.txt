此项目包括对雷神、微鲸、电视猫数据做前处理的forest程序的部署包及其部署脚本

--安装包分发
ansible-playbook -i forest.host install_forest.yml -t install

--配置分发
ansible-playbook -i forest.host install_forest.yml -t config

#启动与检查操作

--启动
helios平展化进程(logcenter)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh helios_product_start.sh'"
medusa平展化进程(logcenter)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh medusa_product_start.sh'"
雷神平展化进程
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh whaley_thorprobe_start.sh'"
电视猫点播直播播放质量
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh medusa_playqos_start.sh'"
helios平展化进程(nginx)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh nginx_helios_product_start.sh'"
medusa平展化进程(nginx)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh nginx_medusa_product_start.sh'"


--停止
helios平展化进程(logcenter)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh helios_product_stop.sh'"
medusa平展化进程(logcenter)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh medusa_product_stop.sh'"
helios平展化进程(nginx)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh nginx_helios_product_stop.sh'"
medusa平展化进程(nginx)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh nginx_medusa_product_stop.sh'"


--重启 helios平展化进程(logcenter)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh helios_product_restart.sh'"
--重启 medusa平展化进程(logcenter)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh medusa_product_restart.sh'"
--重启 雷神平展化进程
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh whaley_thorprobe_restart.sh'"
--重启 电视猫点播直播播放质量
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'cd /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin;sh medua_playqos_restart.sh'"

--检查 helios平展化进程(logcenter)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'ps -ef|grep cn.whaley.turbo.forest.main.HeliosLogProcessingNewApp2|grep -v grep'"
--检查 medusa 平展化进程(logcenter)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'ps -ef|grep cn.whaley.turbo.forest.main.MedusaLogProcessingNewApp2|grep -v grep'"
--检查 雷神 平展化进程
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'ps -ef|grep cn.whaley.turbo.forest.main.ThorProbeLogProcessingApp2|grep -v grep'"
--检查 电视猫点播直播播放质量
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'ps -ef|grep cn.whaley.turbo.forest.main.MedusaPlayqosProcessingApp|grep -v grep'"
--检查 jar包一致性
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'md5sum /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/lib/Forest-1.0.0-SNAPSHOT.jar'"
--检查 helios平展化进程(nginx)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'ps -ef|grep cn.whaley.turbo.forest.main.NginxHeliosLogProcessingApp|grep -v grep'"
--检查 medusa 平展化进程(nginx)
ansible run-apps-machine -i forest.host -mshell -a"su - moretv -c  'ps -ef|grep cn.whaley.turbo.forest.main.NginxMedusaLogProcessingApp|grep -v grep'"



--cronjob分发
ansible run-apps-machine -i forest.host -m cron -a "name='forest autostart job 1' minute=*/6  user='moretv' job=' . /etc/profile;sh /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin/helios_product_start.sh > /dev/null 2>&1'  "
ansible run-apps-machine -i forest.host -m cron -a "name='forest autostart job 2' minute=*/6  user='moretv' job=' . /etc/profile;sh /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin/medusa_product_start.sh > /dev/null 2>&1'  "
ansible run-apps-machine -i forest.host -m cron -a "name='forest autostart job 3' minute=*/6  user='moretv' job=' . /etc/profile;sh /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin/whaley_thorprobe_start.sh > /dev/null 2>&1'  "
ansible run-apps-machine -i forest.host -m cron -a "name='forest autostart job 4' minute=*/6  user='moretv' job=' . /etc/profile;sh /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin/medusa_playqos_start.sh > /dev/null 2>&1'  "


#创建基本topic
ssh bigdata-appsvr-130-1
cd /opt/kafka3
bin/kafka-topics.sh --create --topic helios-pre-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 18
bin/kafka-topics.sh --create --topic helios-processed-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 18
bin/kafka-topics.sh --create --topic medusa-pre-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 48
bin/kafka-topics.sh --create --topic medusa-processed-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 48
bin/kafka-topics.sh --create --topic helios-pre-error-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 18
bin/kafka-topics.sh --create --topic medusa-pre-error-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 18
bin/kafka-topics.sh --create --topic medusa-pre-error-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 18


#查看kafka消费信息
ssh bigdata-appsvr-130-1
cd /opt/kafka3;bin/kafka-console-consumer.sh --topic   helios-pre-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head
cd /opt/kafka3;bin/kafka-console-consumer.sh --topic   helios-processed-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head
cd /opt/kafka3;bin/kafka-console-consumer.sh --topic   medusa-pre-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head
cd /opt/kafka3;bin/kafka-console-consumer.sh --topic   medusa-processed-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head
cd /opt/kafka3;bin/kafka-console-consumer.sh --topic   helios-pre-error-log  -bootstrap-server bigdata-appsvr-130-1:9094 | head
cd /opt/kafka3;bin/kafka-console-consumer.sh --topic   medusa-playqos-output-product  -bootstrap-server bigdata-appsvr-130-1:9094 | head


--------------------日志平展化----------------------
项目目的:处理kafka中log，实时平展化
运行用户:moretv
运行机器:bigdata-appsvr-130-5,bigdata-appsvr-130-6
运行目录:/opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin
运行脚本:
        a.电视猫
          sh bin/medusa_product_restart_v2.sh
        b.电视
          sh bin/helios_product_restart_v2.sh
日志位置:/data/logs/forest-bi
电视猫main方法入口:  cn.whaley.turbo.forest.main.MedusaLogProcessingNewApp2
电视main方法入口:    cn.whaley.turbo.forest.main.HeliosLogProcessingNewApp2



--------------------雷神----------------------
此项目包括对雷神forest程序的部署包及其部署脚本
1.检查kafka3上是否存在topic:helios-processed-log（bigdata-appsvr-130-1）
2.检查kafka3上是否存在topic:thor-probe-log
若无,首先创建topic(replication-factor,partition 根据实际情况配置)
./kafka-console-producer.sh --broker-list bigdata-appsvr-130-1:9094 --topic  helios-pre-log
//创建thor-probe-log
/opt/kafka3/bin/kafka-topics.sh --create --topic helios-pre-log --zookeeper bigdata-appsvr-130-1:2183 --replication-factor 2 --partition 6
//查看thor-probe-log 接收数据
cd /opt/kafka3;bin/kafka-console-consumer.sh --topic   thor-probe-log  --from-beginning  -bootstrap-server bigdata-appsvr-130-1:9094
//查看topic
cd /opt/kafka3;bin/kafka-topics.sh --list --zookeeper bigdata-appsvr-130-1:2183
cd /opt/kafka3;
bin/kafka-topics.sh --topic thor-probe-log  --describe --zookeeper bigdata-appsvr-130-1:2183



#--------------------单台机器部署，监控实时处理延迟----------------------
*/15 * * * * source /etc/profile;sh /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin/monitor_process_delay.sh medusa-processed-log > /dev/null 2>&1
*/16 * * * * source /etc/profile;sh /opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/bin/monitor_process_delay.sh helios-processed-log > /dev/null 2>&1

临时备份，后期删除
moretv@bigdata-appsvr-130-6
/opt/forest-bi/Forest-1.0.0-SNAPSHOT-bin/lib
备份Forest-1.0.0-SNAPSHOT.jar.bakcup.20170823


---目前--
medusa日志处理，4，5，6，7，8，9六台机器，每台启动8个线程，对应medusa-pre-log的48个partition，处理后，写入medusa-processed-log的70个partition(70 partition是后来alert出来的)



--nginx配置分发
ansible-playbook -i forest.host install_forest.yml -t config_for_nginx
ansible-playbook -i forest.host install_forest.yml -t config_for_stop
