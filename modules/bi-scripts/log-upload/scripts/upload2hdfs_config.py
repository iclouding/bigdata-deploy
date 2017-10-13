# -*- coding: utf-8 -*-

paths=['/data/logs/logcenter/current/']


sendto="peng.tao@whaley.cn"
#sendto="lian.kai@whaley.cn,peng.tao@whaley.cn,wang.baozhi@whaley.cn"
logs="/tmp/upload2hdfs.log"
hours=48

filename_match="_bigdata-extsvr,_dbigdd"

hdfs_change={"helios":"whaley"}
retry=2
debug=True