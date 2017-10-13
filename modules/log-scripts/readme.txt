此项目包括日志备份和日志上传脚本的部署包及其部署脚本

#安装Python模块依赖
ansible-playbook -i extsvr.hosts log-scripts.yml -t install_dependency

#初次安装脚本
ansible-playbook -i extsvr.hosts log-scripts.yml -t install

#设定定时调度crontab
ansible-playbook -i extsvr.hosts log-scripts.yml -t cron

#更新脚本
ansible-playbook -i extsvr.hosts log-scripts.yml -t update

