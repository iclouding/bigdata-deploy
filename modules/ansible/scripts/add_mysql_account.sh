mysql -hlocalhost -uroot -p'moretvsmarTV@608_810' <<MYSQL
GRANT ALL ON *.* TO 'dbmanager'@'10.19.15.127' IDENTIFIED BY 'moretvsmarTV@608_810' WITH GRANT OPTION;
flush privileges
MYSQL
