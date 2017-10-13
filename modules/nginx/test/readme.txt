while read -r LINE
do
    echo $LINE
    #echo $LINE > /tmp/req.tmp
    #ab -c 1 -n 1 -H "Content-Type:application/json" -p /tmp/req.tmp http://logupload.aginomoto.com:8180/
done <  ngx_extsvr_log_post_data.txt


while read -r LINE
do
    echo $LINE
    #echo $LINE > /tmp/req.tmp
    #ab -c 1 -n 1 -H "Content-Type:application/json" -p /tmp/req.tmp http://logupload.aginomoto.com:8180/
done <  ngx_extsvr_log_get_data.txt


curl http://log.moretv.com.cn:81/uploadlog?source=test2
ansible ngx-extsvr-log -i nginx.hosts -mshell -a"ls -al /data/logs/nginx/log*.moretv.log"
ansible ngx-extsvr-log -i nginx.hosts -mshell -a"cat /data/logs/nginx/log.moretv.log"

curl http://logupload.aginomoto.com:81/uploadlog?source=logupload_aginomoto_test1
ansible ngx-extsvr-log -i nginx.hosts -mshell -a"ls -al /data/logs/nginx/log*.aginomoto.com"
ansible ngx-extsvr-log -i nginx.hosts -mshell -a"cat /data/logs/nginx/log.moretv.log"

/********************** medusa **********************/
==post
export location=
export location="$location /medusalog"

while read -r LINE
do
    echo $LINE
    #echo $LINE > /tmp/req.tmp
    #ab -c 1 -n 1 -H "Content-Type:application/json" -p /tmp/req.tmp http://logupload.aginomoto.com:8180/
done <  ngx_extsvr_log_post_data.txt

==get
export location=
export location="$location /activity"
export location="$location /medusalog"
export location="$location /uploadlog"
export location="$location /uploadplaylog"
export location="$location /mtvkidslog"
export location="$location /promotionqrcode"
export location="$location /contentqrcode"
export location="$location /accountlog"
export location="$location /user/Service/accountLogin"
export location="$location /weixinlog"
export location="$location /metislog"
export location="$location /test/metislog"
export location="$location /danmulog"
export location="$location /mobilelog"
export location="$location /mobilehelperlog"


/********************** whaleytv **********************/
==post
/
/playqoslog

==get
/test/upgradelog
/moretv/userdurationlog

--whaleyvr
==get
/
==post
/vrapplog

--crawler
==post
/ciscontentcoverage
/price



/****************test-wlslog*********************/
curl -H "forwardhost:log.moretv.com.cn" \
    -d "{\"logType\":\"test哈\"}" \
    http://test-wlslog.aginomoto.com/medusalog

curl -k -H "forwardhost:log.moretv.com.cn" \
    -d "{\"logType\":\"test\"}" \
    https://test-wlslog.aginomoto.com/medusalog

curl http://test-wlslog.aginomoto.com/env

curl -k https://test-wlslog.aginomoto.com/env


###lua log###
log_format lualog "$lualog";
server {
    listen       82;
    location /lualog {
        access_log logs/lualog.log lualog;
        set $lualog '';
        log_by_lua_block {
            local json = require "cjson"
            ngx.var.lualog = json.encode({my_json_data = 1})
        }
    }
}

curl -d "{\"logType\":\"test哈\"}" http://127.0.0.1:82/lualog
curl   http://127.0.0.1:82/lualog

vim conf/online/nginx_http.conf
./sbin/nginx -s reload
