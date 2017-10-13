此项目包括zeppelin相关的部署包及其部署脚本

1.安装包下发
    #安装包太大，只能先手动下发
    scp /data/tools/ansible/modules/zeppelin/package/zeppelin-0.5.6.tgz bigdata-appsvr-130-7:/tmp
    ansible-playbook -i zeppelin.host install_zeppelin.yml -t install

2.配置分发
    ansible-playbook -i zeppelin.host install_zeppelin.yml -t config

3.启动应用
    #启动后，使用请，需要在编译器配置界面，配置相关的spark master地址
    ansible zeppelin -i zeppelin.host -mshell -a"su - hadoop -c  '/opt/zeppelin/bin/zeppelin-daemon.sh start'"

    #启动zeppelin-rom前，需要替换notebook目录，具体命令如下：
    scp /data/tools/ansible/modules/zeppelin/package/notebook.tar.gz bigdata-appsvr-130-7:/tmp
    ssh bigdata-appsvr-130-7
    su - hadoop
    cd /opt/zeppelin-rom/
    rm -rf notebook/
    tar -zxvf /tmp/notebook.tar.gz -C ./
    ansible zeppelin-rom -i zeppelin.host -mshell -a"su - hadoop -c  '/opt/zeppelin-rom/bin/zeppelin-daemon.sh start'"

4.停止应用
    ansible zeppelin -i zeppelin.host -mshell -a"su - hadoop -c  '/opt/zeppelin/bin/zeppelin-daemon.sh stop'"
    ansible zeppelin-rom -i zeppelin.host -mshell -a"su - hadoop -c  '/opt/zeppelin-rom/bin/zeppelin-daemon.sh stop'"

5.重启应用
    ansible zeppelin -i zeppelin.host -mshell -a"su - hadoop -c  '/opt/zeppelin/bin/zeppelin-daemon.sh restart'"
    ansible zeppelin-rom -i zeppelin.host -mshell -a"su - hadoop -c  '/opt/zeppelin-rom/bin/zeppelin-daemon.sh restart'"




