以下功能指令均需在/data/tools/ansible/modules/bi-scripts/mysql2redis/playbook中执行

--安装包分发
ansible mysql2redis-node -i mysql2redis.host -m shell -a "rm -f /opt/bi/mysql2redis/.install"
ansible-playbook -i mysql2redis.host install_mysql2redis.yml -t install


--配置分发
ansible-playbook -i mysql2redis.host install_mysql2redis.yml -t config
ansible-playbook -i mysql2redis.host upload_config.yml -t test
ansible-playbook -i mysql2redis.host upload_config.yml -t product

--添加crontab任务
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-tvservice.mtv_channel-1" minute=30 hour=23 day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis_tvservice.mtv_channel-1"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-tvservice.mtv_channel-0" minute=0 hour=* day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis_tvservice.mtv_channel-0"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-tvservice.mtv_subject-1" minute=30 hour=23 day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis_tvservice.mtv_subject-1"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-mtv_cms.sailfish_sport_match-1" minute=30 hour=23 day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis_mtv_cms.sailfish_sport_match-1"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-mtv_cms.sailfish_sport_match-0" minute=0 hour=* day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis_mtv_cms.sailfish_sport_match-0"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-mtv_cms.mtv_basecontent-1" minute=30 hour=23 day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis_mtv_cms.mtv_basecontent-1"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-mtv_cms.mtv_basecontent-0" minute=*/5 hour=* day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis_mtv_cms.mtv_basecontent-0"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-tvservice_helio.mtv_program-1" minute=15 hour=23 day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis-tvservice_helio.mtv_program-1"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-tvservice_helio.mtv_program-0" minute=30 hour=* day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis-tvservice_helio.mtv_program-0"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-tvservice_mtv.mtv_program-1" minute=15 hour=23 day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis-tvservice_mtv.mtv_program-1"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-tvservice_mtv.mtv_program-0" minute=30 hour=* day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis-tvservice_mtv.mtv_program-0"'

ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-tvservice_helio_forai.mtv_program-1" minute=15 hour=23 day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis-tvservice_helio_forai.mtv_program-1"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-tvservice_helio_forai.mtv_program-0" minute=30 hour=* day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis-tvservice_helio_forai.mtv_program-0"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-tvservice_mtv_forai.mtv_program-1" minute=15 hour=23 day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis-tvservice_mtv_forai.mtv_program-1"'
ansible mysql2redis-node -i mysql2redis.host -m cron -a 'user=spark name="mysql2redis-tvservice_mtv_forai.mtv_program-0" minute=30 hour=* day=* month=* weekday=* job="sh /opt/bi/mysql2redis/bin/launch.sh mysql2redis-tvservice_mtv_forai.mtv_program-0"'


--test
ssh bigdata-appsvr-130-6
/opt/bi/mysql2redis/bin/launch.sh mysql2redis_tvservice.mtv_channel-0 && tail -200f /data/logs/bi/mysql2redis/com.whaley.mysql2redis.Main.log
