此项目包括nginx（服务应用web反向代理、接口服务web反向代理、日志接收服务）的部署包及其部署脚本

--服务&应用集群web反向代理服务
ansible-playbook -i nginx-test.hosts install_ngx-appsvr-webproxy-test.yml
