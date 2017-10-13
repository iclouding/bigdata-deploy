#!bin/bash
wget http://10.10.114.116/whaley_tools/rpmrepo/7/Moretv_mysql-5.7.17.tar.gz -P /data/tools
cd /data/tools
tar -zxvf Moretv_mysql-5.7.17.tar.gz && cd Moretv_mysql-5.7.17 && sh install_mysql.sh
cd /
rm -f /data/tools/Moretv_mysql-5.7.17.tar.gz
rm -rf /data/tools/Moretv_mysql-5.7.17