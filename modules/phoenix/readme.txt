
ansible all -i phoenix.host -m shell -a "rm -f /app/apache-phoenix-4.10.0-HBase-1.2-bin/.install"
ansible all -i phoenix.host -m shell -a "mv /opt/hbase/lib/phoenix-4.8.1-HBase-1.2-server.jar /opt/hbase/lib/phoenix-4.8.1-HBase-1.2-server.jar.bk"
ansible all -i phoenix.host -m shell -a "mv /app/apache-phoenix-4.10.0-HBase-1.2-bin/bin/hbase-site.xml /app/apache-phoenix-4.10.0-HBase-1.2-bin/bin/hbase-site.xml.bk"


ansible all -i phoenix.host -m shell -a "rm -f /opt/hive/lib/phoenix-hive-4.10.0-HBase-1.2.jar"
ansible all -i phoenix.host -m shell -a "rm -f /opt/hive/lib/phoenix-hive-4.10.0-HBase-1.2-sources.jar"

ansible all -i phoenix.host -m shell -a "mv /app/apache-phoenix-4.8.2-HBase-1.2-bin/bin/hbase-site.xml /app/apache-phoenix-4.8.2-HBase-1.2-bin/bin/hbase-site.xml.bk"


#phoenix
ansible-playbook -i phoenix.host install_phoenix.yml -t install
ansible-playbook -i phoenix.host install_phoenix.yml -t config
ansible-playbook -i phoenix.host install_phoenix.yml -t updatejar
ansible-playbook -i phoenix.host install_phoenix.yml -t link

ansible-playbook -i phoenix.host install_phoenix_4.8.2.yml -t install
ansible-playbook -i phoenix.host install_phoenix_4.8.2.yml -t config
ansible-playbook -i phoenix.host install_phoenix_4.8.2.yml -t link

#phoenix queryserver
#bin/queryserver.py [start|stop]
ansible queryserver -i phoenix.host -m shell -a "su - hadoop -c '/opt/phoenix/bin/queryserver.py stop'"
ansible queryserver -i phoenix.host -m shell -a "su - hadoop -c '/opt/phoenix/bin/queryserver.py start'"
ansible queryserver -i phoenix.host -m shell -a "ps -ef|grep -i phoenix |grep -i queryserver"

