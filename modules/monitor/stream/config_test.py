# -*- coding: utf-8 -*-

sendto = 'peng.tao@whaley.cn'
# sendto='peng.tao@whaley.cn,fang.dong@whaley.cn'
streaming = [
             {'hosts': 'bigdata-appsvr-130-3', 'type': 'ps_keyword', 'keyword': 'MoreTV_FrontPageOnlineSidGeneration Moretv_InterestRecommend',
              'users': 'spark', 'commands': 'sh /opt/ai/kafkaIO/shell/MoreTV_InterestOnlineSidGeneration.sh',
              'alter_mail': True}
            ]
