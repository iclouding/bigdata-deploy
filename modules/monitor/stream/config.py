# -*- coding: utf-8 -*-

sendto = 'peng.tao@whaley.cn'
# sendto='peng.tao@whaley.cn,fang.dong@whaley.cn'
streaming = [{'hosts': 'bigdata-appsvr-130-3', 'type': 'yarn_list', 'keyword': 'interest-onlineALS', 'users': 'spark',
             'commands': 'sh /opt/ai/interestOptimization-201707/release/bin/onlineALS.sh', 'alter_mail': True},
            {'hosts': 'bigdata-appsvr-130-3', 'type': 'yarn_list', 'keyword': 'interest-online-user-actions',
             'users': 'spark', 'commands': 'sh /opt/ai/interestOptimization-201707/release/bin/online-user-actions.sh','alter_mail': True},
            {'hosts': 'bigdata-appsvr-130-5', 'type': 'yarn_list', 'keyword': 'interest-online-sid-generation', 'users': 'spark',
             'commands': 'sh /opt/ai/interestOptimization-201707/release/bin/online-sid-generation.sh','alter_mail': True},
            {'hosts': 'bigdata-appsvr-130-5', 'type': 'yarn_list', 'keyword': 'interest-online-long-videos',
             'users': 'spark',
             'commands': 'sh /opt/ai/interestOptimization-201707/release/bin/online-long-videos.sh',
             'alter_mail': True},
             {'hosts': 'bigdata-appsvr-130-3', 'type': 'ps_keyword', 'keyword': 'MoreTV_FrontPagePersonal  Moretv_InterestRecommend',
              'users': 'spark', 'commands': 'sh /opt/ai/kafkaIO/shell/MoreTV_InterestOptimizationOffline.sh',
              'alter_mail': True},
             {'hosts': 'bigdata-appsvr-130-3', 'type': 'ps_keyword', 'keyword': 'MoreTV_FrontPagePersonalOnline  Moretv_InterestRecommend',
              'users': 'spark', 'commands': 'sh/opt/ai/kafkaIO/shell/MoreTV_InterestOptimizationOnline.sh',
              'alter_mail': True},
             {'hosts': 'bigdata-appsvr-130-3', 'type': 'ps_keyword', 'keyword': 'MoreTV_FrontPageOnlineSidGeneration  Moretv_InterestRecommend',
              'users': 'spark', 'commands': 'sh /opt/ai/kafkaIO/shell/MoreTV_InterestOnlineSidGeneration.sh',
              'alter_mail': True}
            ]
