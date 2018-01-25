此项目包括kafka（包括0.8.2和0.10.0.0两个版本）的部署包及其部署脚本
一、启动
1.按照storm.host文件中定义的主机进行分发tar包和配置文件

注意：
        playbook/install_kafka_bin_{1,2,3}.yml: 是修改kafka启动文件，设置：KAFKA_HEAP_OPTS="-Xmx4G -Xms4G";kafka关闭脚本
        config/kafka{1,2,3}: 新的kafka启动和关闭文件

2.执行命令
   第一步：进入所有部署机器执行以下命令
        su - moretv
        cd /opt/kafka
       ./bin/kafka-server-start.sh -daemon ./config/server.properties

        或者执行命令
       开启： ansible all -i kafka.host -mshell -a"su - moretv -c 'cd /opt/kafka1/ &&  ./bin/kafka-server-start.sh -daemon ./config/server.properties '"
       关闭： ansible all -i kafka.host -mshell -a"su - moretv -c 'cd /opt/kafka1/ &&  ./bin/kafka-server-stop.sh ./config/server.properties '"
   第二步：验证
        建立topic，测试

3.创建topic
    第一步：使用通用脚本下发createtopic文件夹下的shellwenjian
    第二部：执行sh文件


-------------------------------------------------------------------------------------------------------------------
--追加kafka启动命令到系统启动项
ansible all -i kafka.host -mshell -a"echo 'su - moretv -c \". /etc/profile;cd /opt/kafka2;./bin/kafka-server-start.sh  -daemon ./config/server.properties\"' >> /etc/rc.local"
ansible all -i kafka.host -mshell -a"echo 'su - moretv -c \". /etc/profile;cd /opt/kafka3;./bin/kafka-server-start.sh  -daemon ./config/server.properties\"' >> /etc/rc.local"
ansible all -i kafka.host -mshell -a"echo 'su - moretv -c \". /etc/profile;cd /opt/kafka4;./bin/kafka-server-start.sh  -daemon ./config/server.properties\"' >> /etc/rc.local"

--删除/etc/rc.local中关键字的行
ansible all -i kafka.host -mshell -a" sed -i -e '/kafka-server-start/d' /etc/rc.local "

---------------安装kafka3---------------
使用9094端口
--安装
ansible-playbook -i kafka.host install_kafka_3.yml -t install
--配置
ansible-playbook -i kafka.host install_kafka_3.yml -t config
--定制的启动停止脚本分发
ansible-playbook -i kafka.host install_kafka_bin_3.yml

ansible all -i kafka.host -mcopy -a"src=/data/tools/ansible/modules/kafka/config/kafka3/log4j.properties dest=/opt/kafka3/config  owner=moretv group=moretv mode=644"
ansible all -i kafka.host -mcopy -a"src=/data/tools/ansible/modules/kafka/config/kafka3/kafka-run-class.sh dest=/opt/kafka3/bin   owner=moretv group=moretv mode=755"



--启动、停止单台kafka3系列的某一台
守护进程启动kafka server
cd /opt/kafka3;./bin/kafka-server-start.sh  -daemon ./config/server.properties
停止kafka server
cd /opt/kafka3;./bin/kafka-server-stop.sh

--启动、停止kafka3系列
ansible all -i kafka.host -mshell -a"su - moretv -c 'cd /opt/kafka3 &&  ./bin/kafka-server-stop.sh '"
ansible all -i kafka.host -mshell -a"su - moretv -c 'cd /opt/kafka3 &&  ./bin/kafka-server-start.sh -daemon ./config/server.properties '"

---------------安装kafka4---------------
使用9092端口
--安装
ansible-playbook -i kafka.host install_kafka_4.yml -t install
--配置
ansible-playbook -i kafka.host install_kafka_4.yml -t config
--定制的启动停止脚本分发
ansible-playbook -i kafka.host install_kafka_bin_4.yml
--启动、停止kafka4系列
ansible all -i kafka.host -mshell -a"su - moretv -c 'cd /opt/kafka4 &&  ./bin/kafka-server-stop.sh '"
ansible all -i kafka.host -mshell -a"su - moretv -c 'cd /opt/kafka4 &&  ./bin/kafka-server-start.sh -daemon ./config/server.properties '"

---------------安装kafka2---------------
使用9093端口
--安装
ansible-playbook -i kafka.host install_kafka_2.yml -t install
--配置
ansible-playbook -i kafka.host install_kafka_2.yml -t config
--定制的启动停止脚本分发
ansible-playbook -i kafka.host install_kafka_bin_2.yml
--启动、停止kafka2系列
ansible all -i kafka.host -mshell -a"su - moretv -c 'cd /opt/kafka2 &&  ./bin/kafka-server-stop.sh '"
ansible all -i kafka.host -mshell -a"su - moretv -c 'cd /opt/kafka2 &&  ./bin/kafka-server-start.sh -daemon ./config/server.properties '"


---------------常用命令 ---------------
ansible all -i kafka.host -mshell -a"su - moretv -c 'netstat |grep 9094|wc -l'"
