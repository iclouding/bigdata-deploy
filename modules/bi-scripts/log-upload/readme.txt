1.分发脚本
ansible-playbook -i log-upload.host install_log-upload.yml -t bin

2.设置crontab
#ansible logs -i log-upload.host -m cron -a 'user=spark name="LogBackUp" minute=5 hour=* day=* month=* weekday=* job="#sh /opt/logupload/LogBackUp.sh"'
#ansible logs -i log-upload.host -m cron -a 'user=spark name="LogBackUp_daily" minute=0 hour=0 day=* month=* weekday=* job="#sh /opt/logupload/LogBackUp_daily.sh"'

ansible logs -i log-upload.host -m cron -a 'user=root name="LogBackUp" minute=5 hour=* day=* month=* weekday=* job="sh /opt/logupload/LogBackUp.sh"'
ansible logs -i log-upload.host -m cron -a 'user=root name="LogBackUp_daily" minute=0 hour=0 day=* month=* weekday=* job="sh /opt/logupload/LogBackUp_daily.sh"'
ansible logs -i log-upload.host -m cron -a 'user=root name="ngx-extsvr-log-rotate" minute=0 hour=* day=* month=* weekday=* job="sh /opt/logupload/NginxLogBackup.sh >> /data/logs/logupload/NginxLogBackup.log"'


ansible logs -i log-upload.host -m shell -a 'su - spark -c "crontab -l"'
#MoretvRecommendLogUpload to hdfs，需要在NFS所在机器运行
ansible MoretvRecommendLogUpload -i log-upload.host -m cron -a 'user=spark name="MoretvRecommendLogUpload to hdfs" minute=0 hour=9 day=* month=* weekday=* job="/opt/logupload/MoretvRecommendLogUpload.sh"'

--启动日志上传
ansible logs -i log-upload.host -m shell -a 'su - spark -c "/opt/logupload/LogBackUp_daily.sh"'
ansible logs -i log-upload.host -m shell -a 'su - spark -c "/opt/logupload/LogBackUp_daily.sh 2017-02-24"'
ansible upload -i log-upload.host -m shell -a 'su - spark -c "/opt/logupload/LogUpload_daily.sh"'
ansible upload -i log-upload.host -m shell -a 'su - spark -c "/opt/logupload/LogUpload_daily.sh 2017-02-24"'
ansible logs -i log-upload.host -m shell -a 'su - spark -c "sh /opt/logupload/LogBackUp.sh "'
ansible logs -i log-upload.host -m shell -a 'su - spark -c "/opt/logupload/LogBackUp.sh log.vr.2017-02-24-*_{hostname}*.log"'

nohup ansible logs -i log-upload.host -m shell -a 'su - spark -c "/opt/logupload/LogBackUp.sh log.*.2017-03-08-*_{hostname}*.log"' &
nohup ansible logs -i log-upload.host -m shell -a 'su - spark -c "/opt/logupload/LogBackUp.sh log.*.2017-03-09-*_{hostname}*.log"' &


ansible logs -i log-upload.host -mcopy -a"src=/data/tools/ansible/modules/bi-scripts/log-upload/bin/NginxLogBackupRepair.sh dest=/app/logupload/  owner=spark group=hadoop mode=771"

#补传遗漏的日志文件（0314-0319）
nohup sh /opt/logupload/NginxLogBackupRepair.sh >> /data/logs/logupload/NginxLogBackupRepair.log &
tail -f /data/logs/logupload/NginxLogBackupRepair.log


files=`hadoop fs -ls '/log/*/rawlog/*log.bz2'|awk '{print $8}'`
if [ -z "$files" ]; then
    echo "no file moved"
	exit 0
fi
echo "" > /tmp/logupload.moved.sh
c=`echo $files|tr -s ' ' '\n'|wc -l`
for file in $files
do
	dir=`echo $file |awk -F '/' '{print "/"$2"/"$3"/"$4}'`
	dateStr=$( expr $file : '.*\([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}\).*'|tr -d "-" )
	if [ -n "$dateStr" ]; then
	    echo "hadoop fs -mv $file  $dir/$dateStr" >> /tmp/logupload.moved.sh
	fi
done
echo `date` "moving file " `cat /tmp/logupload.moved.sh|wc -l`
cat /tmp/logupload.moved.sh |awk '{print $5}'|grep -v '^$'|sort -u|uniq|awk '{print "hadoop fs -mkdir -p "$0}' > /tmp/logupload.mkdir.sh
sh /tmp/logupload.mkdir.sh
sh /tmp/logupload.moved.sh
echo `date` "moved file "

#################################################################################
# 冷备方案
# 1. 备份服务器bigdata-appsvr-130-6, bigdata-appsvr-130-7,
#    其/data/backups目录挂载到本地的/data/backups上
# 2. 备份服务器/data/backups/.profile文件作为子描述文件，其中记录backup_host和backup_user
#    变量值，backup脚本每次执行前source该文件
# 3. 冷备切换动作只需要将本地目录重新挂载即可，具体操作参考运维提供的backup目录的mount操作
#
#################################################################################

