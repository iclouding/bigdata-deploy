# -*- coding: utf-8 -*-


#sendto = 'peng.tao@whaley.cn'
sendto='peng.tao@whaley.cn,fang.dong@whaley.cn,liu.wenhai@whaley.cn,yan.junting@whaley.cn,lian.kai@whaley.cn'
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
            {'hosts': 'bigdata-appsvr-130-3', 'type': 'yarn_list', 'keyword': 'BehaviorRecommendUpdate',
             'users': 'spark', 'commands': 'sh /opt/ai/qiquRecommendation/release/bin/behaviorRecommendUpdate.sh','alter_mail': True},
             {'hosts': 'bigdata-appsvr-130-3', 'type': 'pid', 'keyword': 'MoreTV_FrontPagePersonal',
              'users': 'spark', 'commands': 'sh /opt/ai/kafkaIO/shell/MoreTV_InterestOptimizationOffline.sh',
              'alter_mail': True},
             {'hosts': 'bigdata-appsvr-130-3', 'type': 'pid', 'keyword': 'MoreTV_FrontPagePersonalOnline',
              'users': 'spark', 'commands': 'sh /opt/ai/kafkaIO/shell/MoreTV_InterestOptimizationOnline.sh',
              'alter_mail': True},
             {'hosts': 'bigdata-appsvr-130-3', 'type': 'pid', 'keyword': 'MoreTV_FrontPageOnlineSidGeneration',
              'users': 'spark', 'commands': 'sh /opt/ai/kafkaIO/shell/MoreTV_InterestOnlineSidGeneration.sh',
              'alter_mail': True},
              {'hosts': 'bigdata-appsvr-130-4', 'type': 'pid', 'keyword': 'QiquRecommendStream',
              'users': 'spark', 'commands': 'sh /opt/ai/qiqu_recommend/shell/QiquRecommendStream.sh',
              'alter_mail': True},
              {'hosts': 'bigdata-appsvr-130-4', 'type': 'pid', 'keyword': 'Kafka2CouchBase4QiquRecommendOnline',
              'users': 'spark', 'commands': 'sh /opt/ai/qiqu_recommend/shell/Kafka2CouchBase4QiquRecommendOnline.sh',
              'alter_mail': True}
            ]
