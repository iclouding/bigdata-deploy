#分发
ansible-playbook -i forest-dist.host install_forest-dist.yml -t install
ansible-playbook -i forest-dist.host install_forest-dist.yml -t config
ansible-playbook -i forest-dist.host install_forest-dist.yml -t link
ansible-playbook -i forest-dist.host install_forest-dist.yml -t updatejar


#启动任务
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh start --taskName=medusa ' "
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh start --taskName=whaleytv ' "
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh start --taskName=whaleyvr_orca ' "
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh start --taskName=eagle_mobilehelper ' "
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh start --taskName=crawler ' "
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh start --taskName=whaley_other ' "


#停止任务
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh stop --taskName=medusa ' "
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh stop --taskName=whaleytv ' "
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh stop --taskName=whaleyvr_orca ' "
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh stop --taskName=eagle_mobilehelper ' "
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh stop --taskName=crawler ' "
ansible forest-dist -i forest-dist.host -m shell -a" su - hadoop -c  'cd /opt/forest-dist; ./sbin/launch_msgproc.sh stop --taskName=whaley_other ' "



#other
ansible forest-dist -i forest-dist.host -m shell -a"ps -ef|grep MsgProc|grep -v grep|wc -l"
ansible forest-dist -i forest-dist.host -m shell -a"ps -ef|grep MsgProc|awk '{print \$2}'|grep -v grep|xargs kill"
ansible forest-dist -i forest-dist.host -m shell -a"rm -f /data/logs/forest-dist/*"
ansible forest-dist -i forest-dist.host -m shell -a"chown -R hadoop:hadoop /app/forest-dist"




