cd `dirname $0`
ps -ef|grep hue|grep -v grep| awk '{print $2}'|xargs kill -9
export CLASSPATH=/opt/phoenix/phoenix-4.10.0-HBase-1.2-client.jar:/opt/hue/desktop/conf/log4j.properties:/opt/phoenix/phoenix-4.10.0-HBase-1.2-thin-client.jar:$CLASSPATH
nohup ./supervisor &
