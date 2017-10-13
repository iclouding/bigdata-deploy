此项目包括BI调度平台的部署包及其部署脚本

1.安装包下发
    ansible-playbook -i illidan.host install_illidan.yml -t install

2.配置分发
    ansible-playbook -i illidan.host install_illidan.yml -t config

3.启动前准备
    3.1启动前需要确认NodeJS已安装，并已安装forever插件
    3.2BISparkStatistics.jar需要更新内部的配置

4.启动应用
    ansible illidan -i illidan.host -mshell -a"su - moretv -c  '/opt/illidan/startup.sh'"

5.重启 or 停止 应用
    详见confluence地址：http://172.16.17.100:8090/pages/viewpage.action?pageId=3833953


