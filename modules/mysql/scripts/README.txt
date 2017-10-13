mysql-account.py:
   运行命令 ./mysql-account.py bigdata-appsvr-130-7（参数）
   脚本功能：从123.59.83.223的bigdata数据库的mysql_account表中匹配host信息（如bigdata-appsvr-130-7）
   按返回值在参数对应的服务器的Mysql实例添加相应账号
本质是拼凑命令行如下：
Starting run: mysql -umiles -paspect -hbigdata-extsvr-db_bi1  -e "grant all on *.* to bi@'%'  IDENTIFIED BY 'mlw321@moretv';"
执行结果如下：
run cmd  output
Run mysql -umiles -paspect -hbigdata-extsvr-db_bi1  -e "grant all on *.* to bi@'%'  IDENTIFIED BY 'mlw321@moretv';" success

安全考虑：
    1、拥有grant 权限的账号只能从管理机发起操作
    2、（后续开发）密码功能的加解密功能，DB存放的密码为密文

