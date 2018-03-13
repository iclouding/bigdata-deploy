# -*- coding: utf-8 -*-
local_paths = '/data/logs/nginx'
# sendto = "peng.tao@whaley.cn"
sendto = "lian.kai@whaley.cn,peng.tao@whaley.cn,wang.baozhi@whaley.cn"
logs = "/data/logs/nginx-upload/nginx2hdfs.log"
hours = 3
step = 2
retry = 2
appids = {"mtvkidslog.moretv": "mtvkids", "log.moretv": "moretv2x", "activity.moretv": "activity",
          "weixinlog.moretv": "weixin", "danmulog.moretv": "danmu",
          "boikgpokn78sb95kjhfrendoj8ilnoi7": "boikgpokn78sb95kjhfrendoj8ilnoi7",
          "boikgpokn78sb95k0000000000000000": "boikgpokn78sb95k0000000000000000",
          "boikgpokn78sb95kjhfrendoepkseljn": "boikgpokn78sb95kjhfrendoepkseljn",
          "boikgpokn78sb95kjhfrendobgjgjolq": "boikgpokn78sb95kjhfrendobgjgjolq",
          "boikgpokn78sb95kicggqhbkepkseljn": "boikgpokn78sb95kicggqhbkepkseljn",
          "boikgpokn78sb95kjhfrendojtihcg26": "boikgpokn78sb95kjhfrendojtihcg26"}

backup_path = "/data/local_backups/old_back"

upload_status_path = "/run_log/ods_origin_logupload"
