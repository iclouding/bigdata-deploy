cd /opt/spark2 && ./sbin/start-thriftserver.sh \
 --properties-file conf/spark-thrift-sparkconf.conf \
 --hiveconf hive.server2.thrift.port=20360
