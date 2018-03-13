此项目包括nginx（服务应用web反向代理、接口服务web反向代理、日志接收服务）的部署包及其部署脚本

--服务&应用集群web反向代理服务
ansible-playbook -i nginx-test.hosts install_ngx-appsvr-webproxy-test.yml


------------nginx升级测试操作[为了满足json支持]------------
测试步骤：
1.安装原有版本nginx
ansible-playbook -i nginx_json_test.hosts install_nginx_json_test_old_version.yml  -t install
ansible-playbook -i nginx_json_test.hosts install_nginx_json_test_old_version.yml  -t config

2.运行模拟持续request程序

3.升级nginx版本
ansible-playbook -i nginx_json_test.hosts install_nginx_json_update.yml -t install
ansible-playbook -i nginx_json_test.hosts install_nginx_json_update.yml -t config

4.查看落地日志是否连续



