#使用Linkedin官网提供的开源组件kafka-monitor进行kafka的监控
git地址：https://github.com/linkedin/kafka-monitor
此监控不是具体监控kafka集群的特定topic状态，而是通过此监控读写一个特定topic来获得kafka集群的性能参数。

###安装信息：
安装用户：root
安装机器：bigdata-appsvr-130-8
安装步骤:
mkdir -p/data/scripts/kafka-monitor/;cd /data/scripts/kafka-monitor/
git clone https://github.com/linkedin/kafka-monitor.git .
修改 build.gradle
     `compile 'org.apache.kafka:kafka_2.11:0.10.2.1'    改为 compile 'org.apache.kafka:kafka_2.10:0.10.1.0'
      compile 'org.apache.kafka:kafka-clients:0.10.2.1' 改为 compile 'org.apache.kafka:kafka-clients:0.10.1.0' `
./gradlew jar

###配置文件[监控单kafka集群]
目前监控kafka3集群
/data/scripts/kafka-monitor/config/single-cluster-monitor.properties

如果配置指定"topic": "single-cluster-monitor"，监控系统会自动创建此topic
Topic:single-cluster-monitor	PartitionCount:12	ReplicationFactor:1

###启动
cd /data/scripts/kafka-monitor
nohup sh   ./bin/kafka-monitor-start.sh config/single-cluster-monitor.properties > /dev/null 2>&1 &

###监控UI
http://bigdata-appsvr-130-8:8000/index.html


查看SingleClusterMonitor的git配置代码：
https://github.com/linkedin/kafka-monitor/blob/5807f460a815f4cd4c93414e3514751b77ff9e46/src/main/java/com/linkedin/kmf/apps/SingleClusterMonitor.java

###监控接口
1.
> curl localhost:8778/jolokia/read/kmf.services:type=produce-service,name=*/produce-availability-avg
   返回值
{"request":{"mbean":"kmf.services:name=*,type=produce-service","attribute":"produce-availability-avg","type":"read"},"value":{"kmf.services:name=single-cluster-monitor,type=produce-service":{"produce-availability-avg":1.0}},"timestamp":1503976293,"status":200}
如果produce-availability-avg的数值小于1，表明有broker出现故障.