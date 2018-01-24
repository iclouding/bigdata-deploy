
此项目包括storm相关的部署包及其部署脚本
一、启动
1.按照storm.host文件中定义的主机进行分发tar包和配置文件
2.执行命令
   第一步：登录nimubus机器，
            执命令行：
                    su - storm
                    cd /opt/storm
                    nohup ./bin/storm nimbus &
   第二步：登录其他supervisor机器
           执行一下命令：
                    su - storm
                    cd /opt/storm
                    nohup ./bin/storm supervisor &
   第三步：登录nimubus机器，
           执命令行：
                    su - storm
                    cd /opt/storm
                    nohup ./bin/storm ui &
           观察UI界面


    ansible all -i storm_supervisor_new.host -mshell -a'su - storm -c "cd /opt/storm && nohup ./bin/storm supervisor 2>&1 &"'