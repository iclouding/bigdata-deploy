此项目包括hue的部署包及其部署脚本
一、环境准备
1.root软件包安装
yum install -y ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi gcc gcc-c++ krb5-devel libxml2-devel libxslt-devel make  openldap-devel python-devel  openssl-devel gmp-devel
yum install -y cyrus-sasl-plain libffi libffi-devel libxslt-python


2.安装mysql数据库，创建hue数据库，
create database hue;
grant all on hue.* to bigdata@'%'  IDENTIFIED BY 'bigdata@whaley666';
用户:bigdata,密码：bigdata@whaley666

二、执行 ansible-playbook -i hue.host install_hue.yml

三、检查下发的配置是否生效

四、安装（以下hadoop用户操作）
1.同步权限
/opt/hue/build/env/bin/hue syncdb
用户名：hue
邮件hue@whaley.cn
密码：hue
注：第一次用的时候会出现让你输入一个这个服务所需要的一个用户名和密码，也就是你待会要登陆这个网站的超级用户和密码
2.同步app数据表
/opt/hue/build/env/bin/hue migrate
3.检查hue库中是否有表存在
五、启动
/opt/hue/build/env/bin/supervisor

访问：
http://10.255.130.7:20200
hue
hue

如何使用hue用户需要在core-site添加hue代理

hadoop/hadoop


#配置重新下发
ansible all -i hue.host -mcopy -a"src=/data/tools/ansible/modules/hue/config/hue.ini dest=/opt/hue/desktop/conf  owner=hadoop group=hadoop mode=755"
ansible-playbook -i hue.host install_hue.yml -t config
ansible all -i hue.host -m shell -a "ps -ef|grep hue|grep -v grep| awk '{print \$2}'|xargs kill -9 ; su - hadoop -c '/opt/hue/build/env/bin/launch_supervisor.sh' "

#################################################################################
# 冷备方案
# 1. HUE服务（HUE supervisor进程、LivyServer服务进程）在bigdata-appsvr-130-6, bigdata-appsvr-130-7分别进行了部署，
#    两者可无缝切换，hue.whaley.cn指向两台机器任意一台均可
# 2. HUE服务依赖的数据库目前位于bigdata-appsvr-130-6的hue库，当130-6发送故障，则需要将hue库迁移到其他备份服务器，
#    并修改hue.ini文件中的[[database]]节，并重启supervisor进程
#
#################################################################################

#为了可以在hue的notebook里使用sparksql，需要修改hue的源代码：
/opt/hue/desktop/libs/notebook/src/notebook/connectors/hiveserver2.py
将name='spark-sql'修改成name='sparksql',重启hue

在所部署的机器上重启
ps -ef|grep hue|grep -v grep| awk '{print $2}'|xargs kill -9 ;/opt/hue/build/env/bin/launch_supervisor.sh