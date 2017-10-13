
ansible all -i livy-server.host -m shell -a "rm -f /app/livy-server-0.3.0/.install"


#livy-server
ansible-playbook -i livy-server.host install_livy-server.yml -t install
ansible-playbook -i livy-server.host install_livy-server.yml -t config
ansible-playbook -i livy-server.host install_livy-server.yml -t link

#livy-server
ansible all -i livy-server.host -m shell -a "su - hadoop -c '/opt/livy-server/bin/livy-server stop'"
ansible all -i livy-server.host -m shell -a "su - hadoop -c '/opt/livy-server/bin/livy-server start'"


