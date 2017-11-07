#!/usr/bin/env bash

wget "http://monitor.whaley.cn/whaley_tools/moretv.repo" -P /etc/yum.repos.d/

if [ `ping 10.10.114.116 -c 1 -w 5 | grep 100%  | wc -l` -ge 1 ];then
        REMOTE_HOST="monitor.whaley.cn"
else
        REMOTE_HOST="10.10.114.116"
fi

yum install -y percona-xtrabackup --enablerepo=[moretv]

yum install -y puppet --enablerepo=[moretv]

##设置puppet
#echo '10.10.96.33 moretv-puppet01' >> /etc/hosts
#echo '    server = moretv-puppet01' >> /etc/puppet/puppet.conf
#puppet agent -t

#Install puppet===========================================================END
cd /tmp/
wget "http://${REMOTE_HOST}/whaley_tools/zabbix_agent_whaley.tar.gz"

tar zxf zabbix_agent_whaley.tar.gz

cd zabbix_agent
rpm -ihv zabbix-agent-*.x86_64.rpm --nodeps --force > /dev/null 2>&1
sleep 3

if [ `id zabbix | wc -l` -lt 1 ];then
useradd zabbix -s /sbin/nologin
fi

mv -f zabbix_agentd.conf /etc/zabbix/zabbix_agentd.conf
cp -r scripts/ /etc/zabbix/
mv -f my.cnf-for_zabbix /etc/zabbix/my.cnf
mv -f userparameter_mysql.conf /etc/zabbix/zabbix_agentd.d/

chmod -R u+x /etc/zabbix/scripts/

if [ ! -d /var/log/zabbix ];then
        mkdir -p /var/log/zabbix
        chown -R zabbix.zabbix /var/log/zabbix/
fi

if [ ! -d /var/run/zabbix ];then
        mkdir -p /var/run/zabbix
        chown -R zabbix.zabbix /var/run/zabbix/
fi

VIRTUAL_ROUTE=1
if [[ "$VIRTUAL_ROUTE" = "1" ]];then
	sed -i -e '/^Server=/ s+Server=.*+Server=10.10.154.153+g' /etc/zabbix/zabbix_agentd.conf
	sed -i -e '/^ServerActive=/ s+ServerActive=.*+ServerActive=10.10.154.153:10051+g' /etc/zabbix/zabbix_agentd.conf
fi

ps -ef | grep zabbix_agentd | grep -v grep | while read u p o
do
kill -9 $p
done

sleep 3

/etc/init.d/zabbix-agent start

RESULT=`ps -ef | grep -w zabbix_agentd.conf | grep -v grep | wc -l`

if [ $RESULT -ge 1 ];then
        echo "zabbix_agent installed"
        rm -rf zabbix_agent
else
        /etc/init.d/zabbix-agent restart
fi
#/sbin/chkconfig --add zabbix-agent
##/sbin/chkconfig zabbix-agent on
#systemctl start zabbix-agent.service
#systemctl enable zabbix-agent.service

mkdir -p /data/tools/
cd /data/tools/
#wget http://${REMOTE_HOST}/whaley_tools/agent_install.zip
#unzip agent_install.zip
#cd agent
#./agent install
#
#sed -i 's+10.10.114.116+'$HMS_IP'+g' /data/tools/agent/config/config.ini
##/etc/init.d/agent start
#systemctl start agent.service
#sleep 10
##/etc/init.d/agent restart
#systemctl restart agent.service
#systemctl enable  agent.service
#/sbin/chkconfig --add agent
#/sbin/chkconfig agent on
