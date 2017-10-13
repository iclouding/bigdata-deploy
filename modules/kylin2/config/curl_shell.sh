. /etc/profile;python /opt/kylin/bin/curl_python.py

#on app server 1, cronjob */1 * * * * . /etc/profile;sh /opt/kylin/bin/curl_shell.sh >/data/logs/kylin/curl_shell.log
