日志流量copy灰度测试：

1. 修改nginx_copy.conf文件，增加server_name配置，以确定参与测试的域名
2. 修改杭州机房nginx配置文件，修改监听端口为81，注意只修改参与测试的域名相关配置，修改之前做好备份工作
3. 重启杭州机房现有日志服务nginx进程，启动流量复制nginx进程（sbin/nginx -c conf/nginx_copy.conf）
4. 观察北京机房nginx日志服务是否有相应日志数据产生,同时监控/var/log/nginx/error_copy.log文件

流量拷贝大致步骤：
1.同步流量拷贝的方案给涛哥，涛哥在整个方案实施过程中负责监控（流量、Nginx error log、进程状态、机器负载等）
    和处理带宽等问题
2.人为制造流量测试杭州机房到北京ULB的链路是否正常，顺带测试北京ULB -> nginx -> logcenter -> disk是否正常工作
3.先拿applog.aginomoto.com的流量做灰度测试，观察运行情况，并检验两端数据是否一致
4.上一步通过后，灰度开放至整个微鲸域名（*.aginomoto.com），观察运行情况，并检验两端数据是否一致，重点观察杭州机房的负载
5.上一步通过后，灰度开发至整个电视猫域名（*.moretv.com.cn、*.tvmore.com.cn），和之前一样持续观察


