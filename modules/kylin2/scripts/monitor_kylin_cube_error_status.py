# -*- coding: utf-8 -*-
import json
import requests
from requests.auth import HTTPBasicAuth
import sys

'''
脚本作用：监控kylin1.6版本存在的读取kafka0.10出错，导致cube构建失败的任务，作为补丁存在
输入参数:cube名称 【例如：MEDUSA_PLAY_LIVE_QOS_CUBE】
使用方式：python monitor_kylin_cube_error_satus.py MEDUSA_PLAY_LIVE_QOS_CUBE
部署机器：bigdata-appsvr-130-1
执行用户：hadoop
执行频率：暂定每2分钟运行检测一次
运行方式：cronjob
*/2 * * * * /bin/python /home/hadoop/monitor_kylin_cube_error_satus.py MEDUSA_PLAY_LIVE_QOS_CUBE >>/data/logs/kylin/MEDUSA_PLAY_LIVE_QOS_CUBE_MONITOR.log 2>&1
现有监控cube如下：
MEDUSA_PLAY_LIVE_QOS_CUBE
helios_rolling_status_cube
medusa_hot_play_cube
hot_play_cube
whaley_thor_probe_cube
'''


cube_name=''
for i in range(1, len(sys.argv)):
    cube_name = sys.argv[i]

print(cube_name)
cube_name.split()
url="http://bigdata-appsvr-130-1:7070/kylin/api/jobs"
headers={'user-agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"}
post_data={'username':"ADMIN","passwd":"KYLIN"}
parameters={'cubeName':cube_name,"limit":15,"offset":0,"projectName":"stream","status":8,"timeFilter":1}
P_get=requests.get(url,params=parameters,auth=HTTPBasicAuth('ADMIN', 'KYLIN'))
parsed_json = json.loads(P_get.text)
print(len(parsed_json))
if(len(parsed_json)>0):
    for oneStr in parsed_json:
        if('MERGE' not in oneStr['name'] ):
            print oneStr["name"]
            uuid=oneStr["uuid"]
            url = 'http://bigdata-appsvr-130-1:7070/kylin/api/jobs/'+uuid+'/resume'
            print(url)
            P_put = requests.put(url, auth=HTTPBasicAuth('ADMIN', 'KYLIN'))
            print(P_put)

