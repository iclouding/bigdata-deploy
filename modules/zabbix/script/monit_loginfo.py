# -*- coding: utf-8 -*-
from flask import Flask, render_template
from mmysql import MysqlBase
import time

app = Flask(__name__)


def get_data_mysql(conn, sql):
    m = MysqlBase(**conn)
    data = m.query(sql)
    return data


def return_time():
    base_time = time.time()
    end = base_time + 60
    base_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(base_time))
    end_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(end))
    return base_time, end_time


def write_file(files, data):
    with open(files, 'w')as f:
        f.write(str(data))


@app.route('/more')
def more():
    print "Begin"
    sql = "SELECT 	version,	count(1) AS num FROM loginfo WHERE 	datetime BETWEEN '2017-04-20' AND '2017-04-21' GROUP BY version ORDER BY 	count(1) DESC LIMIT 20"
    conn_data = dict()
    conn_data['db'] = "logcat"
    conn_data['host'] = "172.16.17.164"
    conn_data['user'] = "miles"
    conn_data['pswd'] = "aspect"
    m = MysqlBase(**conn_data)
    data = m.query(sql)
    print data
    return render_template('1.html', data=data)


@app.route('/get_loginfo')
def get_loginfo():
    times_base, time_end = return_time()
    before = "%s 00:00:00" % times_base[0:-6]
    end = "%s 00:00:00" % time_end[0:-6]
    sql_productModel = "select  productModel,count(1) as num from loginfo where datetime between '%s' and '%s' group by  productModel order by count(1) desc limit 10;" % (
        before, end)


@app.route('/')
def hello():
    return "Hello world"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
