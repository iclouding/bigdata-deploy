import requests
import json
url="http://localhost:7070/kylin/api/cubes/MEDUSA_PLAY_LIVE_QOS_CUBE/build2"
data={ "sourceOffsetStart": 0, "sourceOffsetEnd": 9223372036854775807, "buildType": "BUILD"}

headers = {'content-type': 'application/json'}

r=requests.put(url=url,data=json.dumps(data),headers=headers ,auth=('ADMIN', 'KYLIN'),timeout=5)
aa=json.loads(r.text)
print aa