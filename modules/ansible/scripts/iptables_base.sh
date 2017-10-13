#!/bin/bash
iptables -F
iptables -P INPUT DROP
iptables -A OUTPUT -j ACCEPT
iptables -P FORWARD DROP
########INPUT##################################
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -s localhost -d localhost -j ACCEPT
iptables -A INPUT -s 127.0.0.1 -d 127.0.0.1 -j ACCEPT
##################manage##############################
iptables -A INPUT -p tcp -s 10.19.142.67  -j ACCEPT
iptables -A INPUT -p tcp -s 10.10.190.87  -j ACCEPT
iptables -A INPUT -p tcp -s 10.6.30.156  -j ACCEPT
iptables -A INPUT -p tcp -s 10.19.15.127  -j ACCEPT
####################SSHD##############################
#iptables -A INPUT -p tcp -s 172.16.0.0/16 --dport 22 -j ACCEPT
#################PRIVATE NETWORK########################
iptables -A INPUT -p tcp  -s 10.255.128.0/24 -j ACCEPT
iptables -A INPUT -p tcp  -s 10.255.130.0/24 -j ACCEPT
##################DNS#################################
##################DNS##########################
iptables -A INPUT -p udp --dport 53 -j ACCEPT

#################Other service#############################
iptables -A INPUT -p tcp --dport 50070 -j ACCEPT
iptables -A INPUT -p tcp --dport 50075 -j ACCEPT
iptables -A INPUT -p tcp --dport 8088  -j ACCEPT
iptables -A INPUT -p tcp --dport 19888 -j ACCEPT
iptables -A INPUT -p tcp --dport 8188  -j ACCEPT
iptables -A INPUT -p tcp --dport 8042  -j ACCEPT
iptables -A INPUT -p tcp --dport 5050  -j ACCEPT
iptables -A INPUT -p tcp --dport 16010 -j ACCEPT
iptables -A INPUT -p tcp --dport 16030 -j ACCEPT
iptables -A INPUT -p tcp --dport 10000 -j ACCEPT
iptables -A INPUT -p tcp --dport 8095  -j ACCEPT
iptables -A INPUT -p tcp --dport 8081  -j ACCEPT
iptables -A INPUT -p tcp --dport 6060  -j ACCEPT
iptables -A INPUT -p tcp --dport 7070  -j ACCEPT
iptables -A INPUT -p tcp --dport 9200  -j ACCEPT
iptables -A INPUT -p tcp --dport 20210 -j ACCEPT
iptables -A INPUT -p tcp --dport 20211 -j ACCEPT
iptables -A INPUT -p tcp --dport 20200 -j ACCEPT
iptables -A INPUT -p tcp --dport 20220 -j ACCEPT
iptables -A INPUT -p tcp --dport 20250 -j ACCEPT
iptables -A INPUT -p tcp --dport 20251 -j ACCEPT
iptables -A INPUT -p tcp --dport 20252 -j ACCEPT
iptables -A INPUT -p tcp --dport 20253 -j ACCEPT
iptables -A INPUT -p tcp --dport 20254 -j ACCEPT
iptables -A INPUT -p tcp --dport 20260 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
#################PING##########################
iptables -A INPUT -p icmp --icmp-type 0 -j ACCEPT
###############LIMIT####################################
/sbin/sysctl -w net.netfilter.nf_conntrack_max=6553500
