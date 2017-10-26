# -*- coding: utf-8 -*-
import requests

url = "http://127.0.0.1:5000/send-gaoshen-mail"
r = requests.get(url)
if r.status_code == 200:
    print "Success"
else:
    print r.status_code
