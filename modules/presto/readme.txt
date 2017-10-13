- 安装presto
ansible-playbook -i presto.host install_presto.yml -t install

- 下发配置文件
ansible-playbook -i presto.host install_presto.yml -t config

- 启动、停止、重启服务
ansible [all|coordinator|worker] -i presto.host -mshell -a "su - hadoop -c '/opt/presto/bin/launcher [start|stop|restart]'"

- 查看服务状态
ansible [all|coordinator|worker] -i presto.host -mshell -a "su - hadoop -c '/opt/presto/bin/launcher status'"

- 下发可执行文件
ansible-playbook -i presto.host install_presto.yml -t bin

