
#phoenix 正式部署步骤
ansible-playbook -i phoenix_test.host install_phoenix_test.yml -t install
ansible-playbook -i phoenix_test.host install_phoenix_test.yml -t config
ansible-playbook -i phoenix_test.host install_phoenix_test.yml -t updatejar
ansible-playbook -i phoenix_test.host install_phoenix_test.yml -t link


#临时使用，不用于正式部署
ansible-playbook -i phoenix_test.host install_phoenix_test.yml -t rmold
ansible-playbook -i phoenix_test.host install_phoenix_test.yml -t change_owner_tmp

#phoenix queryserver
#bin/queryserver.py [start|stop]
ansible queryserver -i phoenix_test.host -m shell -a "su - hadoop -c '/opt/phoenix/bin/queryserver.py stop'"
ansible queryserver -i phoenix_test.host -m shell -a "su - hadoop -c '/opt/phoenix/bin/queryserver.py start'"
ansible queryserver -i phoenix_test.host -m shell -a "ps -ef|grep -i phoenix |grep -i queryserver"

