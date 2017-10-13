此项目包括lion的部署包及其部署脚本


cd /data/tools/ansible/modules/lion/playbook

ansible-playbook -i lion.host install_lion.yml

ssh bigdata-extsvr-web_bi

su - moretv

/opt/tomcat-lion/bin/catalina.sh start