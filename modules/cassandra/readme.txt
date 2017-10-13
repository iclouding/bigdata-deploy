此项目包括cassandra的部署包及其部署脚本
一、启动
1.按照cassandra.host文件中定义的主机进行分发tar包和配置文件
2.执行命令（启动各节点的cassandra）：ansible all -i cassandra.host -mshell -a"su - moretv -c '/opt/cassandra/bin/cassandra'"
二、验证
   方案一：执行命令：ansible all -i cassandra.host -mshell -a"su - moretv -c 'sh /opt/cassandra/bin/nodetool status'"
   方案二：登录任意一台安装cassandra的机器
           执行一下命令：
            su - moretv
            cd /opt/cassandra
            ./bin/nodetool status