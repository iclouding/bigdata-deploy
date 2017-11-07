#!/bin/bash
#create by ray on 2016-04-26
VIRTUAL_ROUTE=0
DEFAULT_INIT=0
INSTALL_SOFT=0
SHOW_REPOLIST=0

if [[ "$@" =~ "-V" ]];then
	VIRTUAL_ROUTE=1
fi

SCRIPTS_NAME=$0
SCRIPTS_AGRS=$*

HMS_IP="10.10.114.116"

#监控服务器地址
#if [ `ping monitor.whaley.cn -c 1 -w 1 | grep 100%  | wc -l` -ge 1 ];then
if [ `ping 10.10.114.116 -c 1 -w 5 | grep 100%  | wc -l` -ge 1 ];then
        REMOTE_HOST="monitor.whaley.cn"
else
        REMOTE_HOST="10.10.114.116"
fi

if [ `ping $HMS_IP -c 1 -w 5 | grep 100%  | wc -l` -eq 0 ];then
        echo '10.10.114.116     yumrepos.moretv.com.cn' >> /etc/hosts
else
	HMS_IP="123.59.77.3"
fi


rgecho(){
	echo -e "\033[31m $1 \033[0m"
}

ggecho(){
	echo -e "\033[32m $1 \033[0m"
}
gecho(){
        echo -e "\033[45;37m $1 \033[0m"
}

recho(){
        echo -e "\033[41;37m $1 \033[0m"
}

pecho(){
	echo -e "\033[35m $1 \033[0m"
}

becho(){
	echo -e "\033[34m $1 \033[0m"
}

default_init(){
becho "----------------------------------------------------------------------------------------------------"
pecho "欢迎使用该初始化脚本，如果您在使用中遇到任何问题或建议请及时告诉我！！"
becho "----------------------------------------------------------------------------------------------------"

gecho "开始进行初始化。。。。。。"
[[ -f /usr/share/.init.log ]] && rgecho "该机器已经初始化过!" && exit 0;



#yum源
timedatectl set-timezone Asia/Shanghai

yum -y install wget unzip epel-release
#cd /etc/yum.repos.d/
#mkdir bak
#mv ./*.repo bak
#wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.163.com/.help/CentOS7-Base-163.repo
#wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
#wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
wget "http://${REMOTE_HOST}/whaley_tools/moretv.repo" -P /etc/yum.repos.d/
#wget "http://monitor.whaley.cn/whaley_tools/moretv.repo" -P /etc/yum.repos.d/

yum clean all
yum install -y vim net-tools iftop ncftp lsof net-snmp  OpenIPMI nmap telnet yum-plugin-downloadonly systemtap psacct   bind-utils crontabs  openssl-devel pcre-devel zlib-devel  nc  screen ftp lftp iotop   python-psutil MySQL-python m2crypto  numactl libev   MySQL-python m2crypto  python-requests  gcc gcc-c++ make cmake curl curl-devel  sudo ntp ncftp python-devel ntp sysstat  python-pip

echo 'UseDNS  no' >> /etc/ssh/sshd_config
systemctl restart sshd.service

#创建统一目录 data不要分配给HDFS数据盘
mkdir -p /data/tools/
mkdir -p /data/bak/
mkdir -p /data/backup/
mkdir -p /data/webapps/
mkdir -p /data/logs/
#chown -R moretv:moretv /data
chmod 755 /data



#SSH免登陆
cd /root/
mkdir -p .ssh
cat >>/root/.ssh/authorized_keys <<"EOF"
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx8injeUjuJHuZH3belnmG/zpLFAhl4qU7K0I/DMDX3+IAHuwNNqmzNZlYs6+faBmXw/wfonlTFSrbCZtjkDpxDpfH9SUWwpA7HKcjUQMWMLqwnRVVfAW7D6Gc9WoMoIm5MEKUD63Rftu8YTc3aLGXr5JTd1F73+kXxtpf3ckd+WfD4HVdtD94eMhx/e4+/ZhCdkAAkiFfIoXOCHxe5wQ0lfMPLTwYI2l6If2YRqSCiDo3XnvFnixTMCdOif4fpGqYPyGLGPo4rRTRulTP/Fe3pqEBCszDEvANRYy+JS0oMeF92w7XeZaJi50vMapssigPNTYdY+I8XmY2sUqMXywuQ== moretv@SSH-01
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAqxjfl7dKzhf7g1eCOzZ3N2VNxQ/HKf/YP0l4fKooVng1VGcBLkC8LX3H0IU72yeqzMctqmLD0dsICaHRtgLI+opIjOg9krHXTuiCt1uFlwa9/ZA/WUL/CaKQQpRk758toj+S1u9TKbe/OVJRjw/8qwfxebAk6bKqf+LcwPiFlq8WYL1EopvWhJxmTosIXtL/jBRFbclB78bYY5ZyHTaP5dXZFLVGIHQO1+vfas44kRKpxM5EusuE/WNl/18hxsd0jJx2y5hLEhXOmXcgCJpnK2BCB//EdSW251uw43tq9osRb9am43NhkPPDWq4KDbS4hsSLavDxb86jYDqhgdPx5w== root@zabbix_server_01
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCu+uaRIOfLaAdBnxEWrGvNimdNhPgCuOyoMtNQthWfu3+bWFigHMXY8XpKg3VeSL+OoBgojwIMNq2v1c+HmKw+4UPN4A1GnGgQw8WA2GPIf8o7gd1zL4sQSNBtD2LLYwNndKn3whx5xOmOUjYjovRwFIyiSKl9KieVLn3y817bAzZmJrkZ9vLxjP4p8CThITKiinzKHZdCbwuCrbs81FRw9tW38eOXiuE2U5W1SLEcL5++5fzND7uU+U/xMTTMssA28imwhNp+/YYZ/Zb3phiOxWUvsD1UjwDL7JuDCP7UsenYq/9yfpn2WSE6xVGtbuncjsNDUlqt38LhFP+Xjg97
EOF

chmod 700 /root/.ssh/
chmod 600 /root/.ssh/authorized_keys

useradd moretv
chown -R moretv:moretv /data
cd /home/moretv/
mkdir -p .ssh
cat >> /home/moretv/.ssh/authorized_keys <<"EOF"
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx8injeUjuJHuZH3belnmG/zpLFAhl4qU7K0I/DMDX3+IAHuwNNqmzNZlYs6+faBmXw/wfonlTFSrbCZtjkDpxDpfH9SUWwpA7HKcjUQMWMLqwnRVVfAW7D6Gc9WoMoIm5MEKUD63Rftu8YTc3aLGXr5JTd1F73+kXxtpf3ckd+WfD4HVdtD94eMhx/e4+/ZhCdkAAkiFfIoXOCHxe5wQ0lfMPLTwYI2l6If2YRqSCiDo3XnvFnixTMCdOif4fpGqYPyGLGPo4rRTRulTP/Fe3pqEBCszDEvANRYy+JS0oMeF92w7XeZaJi50vMapssigPNTYdY+I8XmY2sUqMXywuQ== moretv@SSH-01
EOF

chmod 700 /home/moretv/.ssh/
chmod 600 /home/moretv/.ssh/authorized_keys
chown moretv:moretv /home/moretv/.ssh/ -R

sed -i -e 's/#RSAAuthentication\ yes/RSAAuthentication\ yes/' /etc/ssh/sshd_config
sed -i -e 's/#PubkeyAuthentication\ yes/PubkeyAuthentication\ yes/' /etc/ssh/sshd_config
sed -i -e 's/#AuthorizedKeysFile/AuthorizedKeysFile/' /etc/ssh/sshd_config
sed -i -e 's/#UseDNS\ yes/UseDNS\ no/' /etc/ssh/sshd_config
sed -i -e '/X11Forwarding yes/s/yes/no/' /etc/ssh/sshd_config

service sshd restart
#systemctl start crond

#关闭selinux
#sed -i -e '/SELINUX=enforcing/s/SELINUX=enforcing/SELINUX=disabled/' /etc/sysconfig/selinux
#setenforce 0

sed -i '/SELINUX/s/enforcing/disabled/' /etc/selinux/config
setenforce 0

#关闭不必要服务

/sbin/chkconfig --level 0123456 ip6tables off


systemctl stop firewalld
systemctl mask firewalld
yum install iptables-services -y
systemctl enable iptables

#设置时间同步服务器
cat >> /var/spool/cron/root << "EOF"
*/30 * * * * /usr/sbin/ntpdate ntp.whaley.cn > /dev/null 2>&1
EOF

cat >> /etc/hosts << "EOF"
10.10.167.158   ntp.whaley.cn
EOF

#修改文件限制
echo "ulimit -SHn 655350" >> /etc/rc.local
cat >> /etc/security/limits.conf << EOF
 *           soft   nofile       655350
 *           hard   nofile       655350
 *           soft   nproc        655350
 *           hard   nproc        655350
EOF



#设置通用内核参数
cp /etc/sysctl.conf /etc/sysctl.conf.bak
cat > /etc/sysctl.conf << EOF
 net.ipv4.ip_forward = 0
 net.ipv4.conf.default.rp_filter = 1
 net.ipv4.conf.default.accept_source_route = 0
 kernel.sysrq = 0
 kernel.core_uses_pid = 1
 net.ipv4.tcp_syncookies = 1
 kernel.msgmnb = 65536
 kernel.msgmax = 65536
 kernel.shmmax = 68719476736
 kernel.shmall = 4294967296
 net.ipv4.tcp_max_tw_buckets = 6000
 net.ipv4.tcp_sack = 1
 net.ipv4.tcp_window_scaling = 1
 net.ipv4.tcp_rmem = 4096 87380 4194304
 net.ipv4.tcp_wmem = 4096 16384 4194304
 net.core.wmem_default = 8388608
 net.core.rmem_default = 8388608
 net.core.rmem_max = 16777216
 net.core.wmem_max = 16777216
 net.core.netdev_max_backlog = 262144
 net.ipv4.tcp_max_orphans = 3276800
 net.ipv4.tcp_max_syn_backlog = 262144
 net.ipv4.tcp_timestamps = 0
 net.ipv4.tcp_synack_retries = 1
 net.ipv4.tcp_syn_retries = 1
 net.ipv4.tcp_tw_recycle = 1
 net.ipv4.tcp_tw_reuse = 1
 net.ipv4.tcp_mem = 94500000 915000000 927000000
 net.ipv4.tcp_fin_timeout = 1
 net.ipv4.tcp_keepalive_time = 1200
 net.ipv4.ip_local_port_range = 30000 65535
 net.ipv6.conf.all.disable_ipv6 = 1
 net.ipv6.conf.default.disable_ipv6 = 1
EOF
/sbin/sysctl -p
echo "sysctl set OK!!"


# Set history
## echo "history command config..."
if ! grep "HISTTIMEFORMAT" /etc/profile >/dev/null 2>&1;then
cat >> /etc/profile << "EOF"
USER_IP=$(who -u am i 2>/dev/null | awk '{print $NF}' |sed -e 's/[()]//g')
HISTDIR=/usr/share/.history
if [ -z $USER_IP ];then
USER_IP=`hostname`
fi
if [ ! -d $HISTDIR ];then
mkdir -p $HISTDIR
chmod 777 $HISTDIR
fi
if [ ! -d $HISTDIR/${LOGNAME} ];then
mkdir -p $HISTDIR/${LOGNAME}
chmod 300 $HISTDIR/${LOGNAME}
fi
export HISTSIZE=4000
DT=$(date +%Y%m%d_%H%M%S)
export HISTFILE="$HISTDIR/${LOGNAME}/$USER_IP.history.$DT"
export HISTTIMEFORMAT="[%Y.%m.%d %H.%M.%S]"
chmod 600 $HISTDIR/${LOGNAME}/*.history* 2>/dev/null
ulimit -c unlimited
EOF
fi

#禁止yum升级系统内核
echo "exclude=kernel*" >> /etc/yum.conf

#安装python的ez_setup.py
cd /tmp/
wget "http://${REMOTE_HOST}/whaley_tools/ez_setup.py"
if [ `ping monitor.whaley.cn -c 1 -w 1 | grep 100%  | wc -l` -ge 1 ];then
	recho "访问外网失败－－！python的easy_install安装失败!"
else
	python ez_setup.py
fi


touch /usr/share/.init.log
echo `date +%F` > /usr/share/.init.log
/usr/bin/chattr +i /usr/share/.init.log

}

change_hostname(){
	HOSTNAME=$1	
	if [ ! -z $HOSTNAME ];then
		`which hostname` $HOSTNAME
		`which sed` -i 's+HOSTNAME=.*+HOSTNAME='$HOSTNAME'+g' /etc/sysconfig/network
        fi
	if [ -f "/etc/init.d/zabbix-agent" ];then
		/etc/init.d/zabbix-agent restart
	fi
}

gecho(){
	echo -e "\033[45;37m $1 \033[0m"
}

recho(){
	echo -e "\033[41;37m $1 \033[0m"
}

print_install_info(){
	gecho " 开始安装$1!!!!!"
	sleep 1
}

yum_install(){
	yum install --enablerepo=moretv -y $1
}

check_process(){
	if  [ `rpm -qa | grep $1 | wc -l` -ge $2 ] && [ ! -z "`whereis $1  | cut -d: -f2`" ];then
        	recho "$1已经安装,请勿重复安装,请使用rpm -qa | grep $1确认。"
         	return 1
	fi
}


system_install(){
	for var in $@
	do
		case $var in
		nginx)
			#yum install -y  -enablerepo=moretv
			print_install_info $var
			check_process $var 1
			if [ $? == 1 ];then
                	continue
                	else
			echo "nginx version error"
			#yum_install Moretv_nginx
			#yum install -y memcached
			#/usr/bin/memcached -p 11211 -u root -m 1024 -c 1024 -d
			fi
			;;
		php|php5)
			print_install_info $var
			check_process $var 1
                        if [ $? == 1 ];then
                        continue
                        else
			yum_install Moretv_php-5.5.30 Moretv_libmemcached Moretv_memcached phpredis
			fi
			;;
		
		tomcat)
			print_install_info $var
			check_process $var 1
                        if [ $? == 1 ];then
                        continue
                        else
			yum_install Moretv_tomcat
			fi
			;;
		php7)
			print_install_info $var
                        check_process $var 1
                        if [ $? == 1 ];then
                        continue
                        else
			yum_install Moretv_php7-0.5 Moretv_libmemcached Moretv_memcached phpredis
                        fi
			;;
#		mysql|Moretv_mysql)
#			print_install_info $var
#			check_process $var 2
#                        if [ $? == 1 ];then
#                        continue
#                        else
#			wget http://$REMOTE_HOST/whaley_tools/rpm/Moretv_mysql-5.5.28.tar.gz -P /data/tools
#			cd /data/tools
#			tar -zxvf Moretv_mysql-5.5.28.tar.gz && cd Moretv_mysql-5.5.28 && sh install_mysql.sh
#			cd /
#			rm -f /data/tools/Moretv_mysql-5.5.28.tar.gz
#			rm -rf /data/tools/Moretv_mysql-5.5.28
#			fi
#			;;
		nodejs|nodejs5)
			print_install_info $var
			check_process $var 1
                        if [ $? == 1 ];then
                        continue
                        else
			yum_install Moretv_nodejs5.2
			fi
			;;
		redis)
			print_install_info $var
                        check_process $var 1
                        if [ $? == 1 ];then
                        continue
                        else
			yum_install Moretv_redis
                        fi
			;;
		*)
			recho "请使用\"yum install\"安装$var"
			;;
	esac
	done
}

show_yumrepo(){
	if ! yum list | grep -w "moretv" > /dev/null 2>&1;then
		echo -e "\033[31m \033[1m \033[5m 还没安装moretv的源，请先安装!!! \033[0m"
		exit
	else
	echo -e "\033[32m 可安装的软件包有以下:"
	yum list | grep -w "moretv" | awk '{print $1}'	
	echo -e "\033[0m"
	fi
}

usage_info(){
	        echo "Usage:$0 -i -n [-V] hostname -a [install soft's name]."
                echo "参数说明:"
		echo "-l:显示自订制的moretv源可安装的软件包。"
                echo "-i:只做初始化安装。"
		echo "-V:当云主机使用虚拟路由器时使用该参数，可使zabbix不探测虚拟路由，使用内网地址。"
                echo "-n:指定要修改的主机名。"
                echo "-a:选择要安装的软件包，多个软件包需要用双引号括起来，如\"$0 -a \"nginx mysql php\"\""
                echo -e "\033[43;31m!!!!!!友情提示!!!!!!\033[0m"
                echo -e "\033[43;31m*安装多个软件包一定记着用引号哟!\033[0m"
                echo -e "\033[43;31m*可安装软件包可以下载安装自订制的yum源查看.\033[0m"
                echo -e "\033[43;31m*下载地址\"http://monitor.whaley.cn/whaley_tools/moretv.repo\".\033[0m"
                echo -e "\033[43;31m*然后你懂得，自己查一下吧！！\033[0m"
}

[[ $# -eq 0 ]] && usage_info

while getopts "Vlih:n:a:" opt;do
    case $opt in
	l)	SHOW_REPOLIST=1;;
		#show_yumrepo;;
	V)	VIRTUAL_ROUTE=1;;
	n) 	HOST_NAME=$OPTARG
        	;;
	i)  DEFAULT_INIT=1
                ;;
	a)
		INSTALL_SOFT=1
		SOFTNAME=$OPTARG	
#		ggecho "你想安装<<$OPTARG>>?"
#		system_install $OPTARG
		;;
        h|*)	usage_info 
                exit 0 ;;
    esac
done

if [ ! -z $HOST_NAME ];then
        change_hostname $HOST_NAME
fi

if [ $DEFAULT_INIT = 1 ];then
	default_init
fi

if [ $INSTALL_SOFT = 1 ];then
	ggecho "你想安装<<$SOFTNAME>>?"
        system_install $SOFTNAME
fi

if [ $SHOW_REPOLIST = 1 ];then
	show_yumrepo
fi
