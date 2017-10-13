#iptables -t nat -A POSTROUTING -s 10.255.128.0/22 -j MASQUERADE
#while read ip
#do
#	iptables -t nat -A POSTROUTING -s $ip -j MASQUERADE
#done </opt/ip.list
#while read ip
#do
#	iptables -t nat -A POSTROUTING -s $ip -j MASQUERADE
#done </opt/ip.list

#!/bin/bash
iptables -F
iptables -P INPUT DROP
iptables -A OUTPUT -j ACCEPT
iptables -P FORWARD DROP
###################NAT################################
iptables -A FORWARD -s 10.255.0.0/16 -o eth0 -j ACCEPT
#iptables -A FORWARD -d 10.255.0.0/16 -m state --state ESTABLISHED,RELATED -i eth0 -j ACCEPT
########INPUT#########################################
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -s localhost -d localhost -j ACCEPT
iptables -A INPUT -s 127.0.0.1 -d 127.0.0.1 -j ACCEPT
iptables -A INPUT -p icmp -m icmp --icmp-type 8 -j ACCEPT
##################manage##############################
iptables -A INPUT -p tcp -s 10.19.142.67  -j ACCEPT
iptables -A INPUT -p tcp -s 10.10.190.87  -j ACCEPT
iptables -A INPUT -p tcp -s 10.6.30.156  -j ACCEPT
iptables -A INPUT -p tcp -s 10.19.15.127  -j ACCEPT
iptables -A INPUT -p tcp -s 10.10.154.153  -j ACCEPT
iptables -A INPUT -p tcp -s 10.10.114.116  -j ACCEPT
iptables -A INPUT -p tcp -s 10.19.164.80  -j ACCEPT
#################PRIVATE NETWORK########################
iptables -A INPUT -p tcp  -s 10.255.128.0/16 -j ACCEPT
iptables -A INPUT -p tcp  -s 10.255.129.0/16 -j ACCEPT
iptables -A INPUT -p tcp  -s 10.255.130.0/16 -j ACCEPT
iptables -A INPUT -p tcp  -s 10.10.0.0/16 -j ACCEPT
iptables -A INPUT -p tcp  -s 10.19.0.0/16 -j ACCEPT
####################SSHD##############################
#iptables -A INPUT -p tcp -s 172.16.0.0/16 --dport 22 -j ACCEPT
##################DNS#################################
iptables -A INPUT -p udp --dport 53 -j ACCEPT
#################Other service########################
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
#################FTP#################################
#################PING#################################
iptables -A INPUT -p icmp --icmp-type 0 -j ACCEPT
###############LIMIT##################################
/sbin/sysctl -w net.netfilter.nf_conntrack_max=6553500
