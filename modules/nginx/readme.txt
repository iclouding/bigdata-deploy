此项目包括nginx（服务应用web反向代理、接口服务web反向代理、日志接收服务）的部署包及其部署脚本

--安装nginx[服务&应用集群]
ansible-playbook -i nginx-appsvr.hosts install_nginx.yml

--服务&应用集群web反向代理服务
ansible-playbook -i nginx.hosts install_ngx-appsvr-webproxy.yml

--对外服务集群web方向代理服务
ansible-playbook -i nginx.hosts install_ngx-extsvr-webproxy.yml

--对外服务集群日志接口服务
ansible-playbook -i nginx.hosts install_ngx-extsvr-log.yml

--对外服务集群日志接口服务(log-v2.0)
ansible-playbook -i nginx-extsvr-v2.0.hosts install_ngx-extsvr-log-v2.0.yml

--[测试环境]对外服务集群日志接口服务(log-v2.0)
ansible-playbook -i nginx-extsvr-v2.0-test.hosts install_ngx-extsvr-log-v2.0-test.yml

--滚动重新加载配置[对外服务集群日志接口服务]
for host in `cat nginx.hosts|grep "bigdata-extsvr-log*"|sort -u|uniq`
do
	echo "reloading $host"
	ssh $host '/opt/openresty/nginx/sbin/nginx -t -c /opt/openresty/nginx/conf/nginx.conf && /opt/openresty/nginx/sbin/nginx -s reload'
	echo "reloaded $host,sleep 3"
	sleep 3
done

--添加日志轮滚脚本
ansible-playbook -i nginx.hosts install_ngx-logrotate.yml
ansible ngx-extsvr-log -i nginx.hosts -m cron -a 'user=root name="ngx-extsvr-log-rotate" minute=0 hour=* day=* month=* weekday=* job="sh /data/tools/nginx_logrotate.sh >> /data/logs/nginx/nginx_logrotate.log"'

--每日nginx重加载一次，解决nginx工作进程内存占用问题
ansible ngx-extsvr-log -i nginx.hosts -m cron -a 'user=root name="ngx-extsvr-reload" minute=30 hour=0 day=* month=* weekday=* job="/opt/openresty/nginx/sbin/nginx -s reload"'


--删除指定日期日志
ansible ngx-extsvr-log -i nginx.hosts -m shell -a "rm -f /data/log_back/170223/_data_logs_nginx*"
ansible ngx-extsvr-log -i nginx.hosts -m shell -a "rm -f /data/log_back/170222"

--挂载备份盘
ansible ngx-extsvr-log -i nginx.hosts -m shell -a "yum install -y nfs-utils nfs-utils-lib"
ansible ngx-extsvr-log -i nginx.hosts -m shell -a "mkdir -p /data/backups ; mount -t nfs  10.255.130.7:/data/backups /data/backups"
/etc/rc.d/rc.local

ansible ngx-extsvr-log -i nginx.hosts -m shell -a "df -h"

ab -n 100000 -c 8000 -p 'post.body' -T 'application/json' 'http://test-logcopy.aginomoto.com/'
apr_socket_recv: Connection reset by peer (104)
Total of 6010 requests completed
解决方案：修改/etc/sysctl.conf,设置
 net.ipv4.tcp_max_syn_backlog = 819200
 sytctl -p

--下发v1.1配置文件并reload
ansible-playbook -i nginx.hosts install_ngx-extsvr-log-v1.1.yml

--下发v1.1 https 配置文件并reload
ansible-playbook -i nginx.hosts install_ngx-extsvr-log-v1.1-https.yml