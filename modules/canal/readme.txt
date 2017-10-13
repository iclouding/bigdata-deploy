#canal安装部署

#安装deployer
ansible-playbook -i canal.deployer.hosts install_canal.deployer.yml -t install
ansible-playbook -i canal.deployer.hosts install_canal.deployer.yml -t link
ansible-playbook -i canal.deployer.hosts install_canal.deployer.yml -t config
ansible-playbook -i canal.deployer.hosts install_canal.deployer.yml -t updatejar

#启动/停止
ansible all -i canal.deployer.hosts -mshell -a 'su - moretv -c "/opt/canal.deployer/bin/stop.sh"'
ansible all -i canal.deployer.hosts -mshell -a 'su - moretv -c "/opt/canal.deployer/bin/startup.sh"'



