# -*- coding: utf-8 -*-

zookeepers_conn = "10.255.130.1:2182"
kafka_conn = "10.255.130.1:9093"
# group = "consumer-group"
# topic_name = ['association_recommend', 'helios-rec4search-userTopContentType']

kafka_info = {"moretv": ['MoreTV_FrontPage']
              }

redis_host = '10.255.130.7'
port = 6380
db = 1
redis_expired = 360000

check_inerval = 3600

#定义监控topic的间隔
monitor_time_interval = {
    'MoreTV_FrontPage': 24,
    'helios-rec4search-userTopContentType': 1
}
#定义2个间隔的topic报警阈值
monitor_values_interval = {
    'MoreTV_FrontPage': 50000,
    'helios-rec4search-userTopContentType': 100000
}
#每个topic独有的报警策略
monitor_sendto = {
    'MoreTV_FrontPage': ['peng.tao@whaley.cn', 'xu.tong@whaley.cn'],
    'helios-rec4search-userTopContentType': ['peng.tao1@whaley.cn', 'xu.tong@whaley.cn']
}
