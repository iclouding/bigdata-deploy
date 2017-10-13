# -*- coding: utf-8 -*-
import requests
import json


def send_alter_mail(sub, body):
    mail_content = dict()
    mail_content["sub"] = sub
    mail_content["content"] = body
    mail_content["sendto"] = "wang.baozhi@whaley.cn"
    mail_url = 'http://10.19.15.127:5006/mail/api/v1.0/send'
    
    heads = {'content-type': 'application/json'}
    r = requests.post(url = mail_url, headers = heads, data = json.dumps(mail_content))
    if r.status_code == 200:
        return True
    else:
        return False


def check_kafka():
    url = "http://localhost:8778/jolokia/read/kmf.services:type=produce-service,name=*/produce-availability-avg"
    
    r = requests.get(url)
    status = r.status_code
    output = r.content
    
    if status == 200:
        try:
            return_value = json.loads(output)['value']['kmf.services:name=single-cluster-monitor,type=produce-service'][
                'produce-availability-avg']
        except:
            return_value = 0
    else:
        return_value = 0
    
    return return_value


def main():
    values = check_kafka()
    print values
    # if float(values) < float(1):
    #     mysub = "Kafka 可用性报警  "
    #     msg = "kafka 可用性为%s,低于预设值" % str(values)
    #     send_alter_mail(mysub, msg)


if __name__ == "__main__":
    try:
        main()
    except:
        
        import StringIO, traceback
        
        fp = StringIO.StringIO()
        traceback.print_exc(file = fp)
        message = fp.getvalue()
        # info = sys.exc_info()
        msg_errror = "脚本运行异常 %s" % message
        mail_sub = "kafka 监控（app_8）脚本运行异常"
        send_alter_mail(sub = mail_sub, body = msg_errror)
