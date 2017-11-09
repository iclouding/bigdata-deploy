#!/bin/bash
iptables -F
iptables -P INPUT DROP
iptables -A OUTPUT -j ACCEPT
iptables -P FORWARD DROP
###################NAT################################

########INPUT#########################################
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -s localhost -d localhost -j ACCEPT
iptables -A INPUT -s 127.0.0.1 -d 127.0.0.1 -j ACCEPT
iptables -A INPUT -p icmp -m icmp --icmp-type 8 -j ACCEPT
##################manage##############################
iptables -A INPUT -p tcp -s 10.19.142.67 -j ACCEPT
iptables -A INPUT -p tcp -s 10.10.190.87 -j ACCEPT
iptables -A INPUT -p tcp -s 10.6.30.156 -j ACCEPT
iptables -A INPUT -p tcp -s 10.19.15.127 -j ACCEPT
iptables -A INPUT -p tcp -s 10.10.154.153 -j ACCEPT
iptables -A INPUT -p tcp -s 10.10.114.116 -j ACCEPT
iptables -A INPUT -p tcp -s 10.19.164.80 -j ACCEPT
####################SSHD##############################
#iptables -A INPUT -p tcp -s 172.16.0.0/16 --dport 22 -j ACCEPT
#################PRIVATE NETWORK########################
iptables -A INPUT -p tcp -s 10.255.128.0/24 -j ACCEPT
iptables -A INPUT -p tcp -s 10.255.130.0/24 -j ACCEPT
iptables -A INPUT -p tcp -s 10.10.0.0/16 -j ACCEPT
iptables -A INPUT -p tcp -s 10.19.0.0/16 -j ACCEPT
##################DNS#################################
iptables -A INPUT -p udp --dport 53 -j ACCEPT
#################Other service########################
#iptables -A INPUT -p tcp --dport 80 -j ACCEPT
#iptables -A INPUT -p tcp --dport 443 -j ACCEPT
#################PING#################################
iptables -A INPUT -p icmp --icmp-type 0 -j ACCEPT
#################office NETWORK#################################


iptables -A INPUT -p tcp -s 180.169.235.10 -j ACCEPT
iptables -A INPUT -p tcp -s 180.169.235.11 -j ACCEPT
iptables -A INPUT -p tcp -s 180.169.235.12 -j ACCEPT
iptables -A INPUT -p tcp -s 180.169.235.13 -j ACCEPT
iptables -A INPUT -p tcp -s 180.169.235.14 -j ACCEPT
iptables -A INPUT -p tcp -s 180.169.235.42 -j ACCEPT
iptables -A INPUT -p tcp -s 180.169.235.43 -j ACCEPT
iptables -A INPUT -p tcp -s 180.169.235.44 -j ACCEPT
iptables -A INPUT -p tcp -s 180.169.235.45 -j ACCEPT
iptables -A INPUT -p tcp -s 180.169.235.46 -j ACCEPT

#iptables -A INPUT -p tcp -s 116.236.232.242 -j ACCEPT
#iptables -A INPUT -p tcp -s 116.236.232.243 -j ACCEPT
#iptables -A INPUT -p tcp -s 116.236.232.244 -j ACCEPT
#iptables -A INPUT -p tcp -s 116.236.232.245 -j ACCEPT
#iptables -A INPUT -p tcp -s 116.236.232.246 -j ACCEPT
iptables -A INPUT -p tcp -s 61.129.122.66 -j ACCEPT
iptables -A INPUT -p tcp -s 180.168.183.186 -j ACCEPT
iptables -A INPUT -p tcp -s 180.168.202.42 -j ACCEPT
iptables -A INPUT -p tcp -s 116.228.159.142  -j ACCEPT
iptables -A INPUT -p tcp -s 180.169.117.162  -j ACCEPT
iptables -A INPUT -p tcp -s 180.169.128.254  -j ACCEPT
################whaley vr ip list######################
iptables -A INPUT -p tcp -s 210.13.81.138 -j ACCEPT
iptables -A INPUT -p tcp -s 116.226.223.136  -j ACCEPT
iptables -A INPUT -p tcp -s 116.226.223.136  -j ACCEPT
iptables -A INPUT -p tcp -s 210.13.89.74  -j ACCEPT
################whaley xiaoshou ip list######################
iptables -A INPUT -p tcp -s 180.169.117.162 -j ACCEPT
iptables -A INPUT -p tcp -s 123.59.131.142  -j ACCEPT
###############LIMIT##################################
/sbin/sysctl -w net.netfilter.nf_conntrack_max=6553500