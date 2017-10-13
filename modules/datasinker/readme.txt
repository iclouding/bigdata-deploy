此项目包括datasinker的部署包及其部署脚本

1.安装包下发
    ansible-playbook -i datasinker.host install_datasinker.yml -t install

2.配置分发
    ansible-playbook -i datasinker.host install_datasinker.yml -t config

3.启动应用
    ansible datasinker-price -i datasinker.host -mshell -a"su - moretv -c  '/opt/datasinker-price/bin/startup.sh'"
    ansible datasinker-cis -i datasinker.host -mshell -a"su - moretv -c  '/opt/datasinker-cis/bin/startup.sh'"

4.停止应用
    ansible datasinker-price -i datasinker.host -mshell -a"su - moretv -c  '/opt/datasinker-price/bin/shutdown.sh'"
    ansible datasinker-cis -i datasinker.host -mshell -a"su - moretv -c  '/opt/datasinker-cis/bin/shutdown.sh'"

5.重启应用
    ansible datasinker-price -i datasinker.host -mshell -a"su - moretv -c  '/opt/datasinker-price/bin/restart.sh'"
    ansible datasinker-cis -i datasinker.host -mshell -a"su - moretv -c  '/opt/datasinker-cis/bin/restart.sh'"




