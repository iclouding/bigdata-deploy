# -*- coding: utf-8 -*-
# !/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.ticker as ticker
import datetime
import MySQLdb
import warnings
import pdb
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
import sys
import ConfigParser


class MysqlBase():
    # 初始化mysql连接
    def __init__(self, ip="10.10.1.1", user="root", passwd='11', databases='zabbix'):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.databases = databases
        try:
            self.conn = MySQLdb.connect(self.ip, self.user, self.passwd, self.databases)
        except:
            raise ValueError("mysql connect failed %s") % self.ip
        self.curs = self.conn.cursor()
        self.curs.execute('SET NAMES utf8')

    def __del__(self):
        self.curs.close()
        self.conn.close()

    def insert(self, table, data):
        _field = ','.join(['`%s`' % (k_insert) for k_insert in data.keys()])
        _value = ','.join(["'%s'" % (self.conn.escape_string(str(v_insert))) for v_insert in data.values()])
        _sql = 'INSERT INTO `%s`(%s) VALUES(%s)' % (table, _field, _value)

        self.curs.lastrowid = 0
        try:
            self.curs.execute(_sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise ValueError("insert error %s" % _sql)

        return self.curs.lastrowid

    def update(self, table, data, condition):
        _field = ','.join(["`%s`='%s'" % (k_update, self.conn.escape_string(str(data[k_update]))) for k_update in data])
        _sql = "UPDATE `%s` SET %s where %s" % (table, _field, condition)

        resNum = 0
        try:
            resNum = self.curs.execute(_sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise ValueError("update error %s" % _sql)

        return resNum

    def delete(self, table, condition):
        _sql = 'DELETE FROM `%s` WHERE %s' % (table, condition)
        resNum = 0
        try:
            resNum = self.curs.execute(_sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise ValueError('delete error %s' % _sql)
        return resNum

    def query(self, sql):
        res = ''
        try:
            self.curs.execute(sql)
            res = self.curs.fetchall()
        except:
            raise ValueError('query error %s' % sql)
        return res

    def change(self, sql, many=False):
        ###过滤unknow table的warning
        warnings.filterwarnings('ignore')
        resNum = 0
        if many:
            try:
                resNum = self.curs.executemany(sql, many)
                self.conn.commit()
            except:
                self.conn.rollback()
                raise ValueError('exec error %s' % sql)
        else:
            try:
                resNum = self.curs.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                raise ValueError('exec error %s' % sql)

        return resNum


class CreatePng():
    def __init__(self, path, items, outpath):
        self.path = path
        self.items = items.split(",")
        self.outpath = outpath

    def create_png_all(self):
        # 画在一张图中
        r = mlab.csv2rec(self.path)
        r.sort()
        N = len(r)
        ind = np.arange(N)  # the evenly spaced plot indices
        ind1 = np.arange(N + 3)
        fig = plt.figure()

        def _format_date(self, x, pos=None):
            if not x % 1 and x < N:
                thisind = np.clip(int(x), 0, N - 1)
                return r.date[thisind].strftime('%Y-%m-%d')
            else:
                return ''

        for i in range(len(self.items)):
            ax = fig.add_subplot(len(self.items), 1, i + 1)
            ax.plot(ind1, ind1, '-', color='white')
            ax.plot(ind, r[self.items[i]], 'o-', label=self.items[i])
            ax.set_title(self.items[i])

            ymin, ymax = min(r[self.items[i]]), max(r[self.items[i]])
            dy = (ymax - ymin) * 0.2
            ax.set_ylim(ymin - dy, ymax + dy)

            ax.xaxis.set_major_formatter(ticker.FuncFormatter(_format_date))
            fig.autofmt_xdate()

            # 显示图片
        plt.savefig(self.outpath)
        return self.outpath


class SendMail():
    def __init__(self, mailto, subject, mail_contenct):
        self.subject = subject
        self.mailto = mailto
        self.mail_contenct = mail_contenct
        self.is_img = is_img

    def send_mail(self):
        # 第三方 SMTP 服务
        mail_host = "smtp.exmail.qq.com"  # 设置服务器
        mail_user = "peng.tao@whaley.cn"  # 用户名
        mail_pass = "tel7206324"  # 口令

        # emailfrom = "peng.tao@whaley.cn"
        emailfrom = "whaley.ops@whaley.cn"
        msg = MIMEMultipart('related')
        msg['From'] = emailfrom
        msg['To'] = self.emailto
        msg['Subject'] = Header(self.subject, 'utf-8')
        if is_img:
            msg = _add_img('/data/tools/regist/send_report/regist.png', 'Active', msg)

        msgText = MIMEText(self.mail_contenct, 'html', 'utf-8')
        msg.attach(msgText)

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            smtpObj.login(mail_user, mail_pass)
            COMMASPACE = ','
            smtpObj.sendmail(emailfrom, emailto.split(","), msg.as_string())
            print "邮件发送成功"
        except smtplib.SMTPException:
            print "Error: 无法发送邮件"


def initlog():
    import logging
    logger = None
    logger = logging.getLogger()
    log_name = sys.argv[0].split(".")[0] + ".log"
    hdlr = logging.FileHandler(log_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return [logger, hdlr]


def logMsg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger, hdlr = initlog()
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)  # 网络上的实现基本为说明这条语句的使用和作用


def _add_img(self, file, imgid, msg):
    text = "新用户&活跃用户 90天数据展示"
    fp = open(file, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    img.add_header('Content-ID', '<%s>' % imgid)
    html = '<html><body><h3 >%s</h3><img src=\"cid:%s\" /></body></html>' % (text, imgid)
    # html = '<html><body><br><img src=\"cid:%s\" border=\"1\"></br></body></html>' % imgid
    content = MIMEText(html, 'html', 'utf-8')
    msg.attach(content)
    msg.attach(img)
    return msg


def get_db_data(ip, user, passwd, databases):
    # sql='select new_num,active_num,totaluser_num from mtv_user_overview where day='2015-12-27';'
    now = get_date(day=0)
    now_b_90 = get_date(day=92)
    sql = "select day,new_num,active_num,totaluser_num from mtv_user_overview where day<'%s' and day>='%s' order by day desc;" % (
    now, now_b_90)
    print sql
    m = MysqlBase(ip=ip, user=user, passwd=passwd, databases=databases)
    try:
        data = m.query(sql)
        return data
    except:
        text = "Get data from DB faild"
        send_alter_mail(text)


def send_alter_mail(text):
    subject = "Check values error by send_report"
    mailto = "peng.tao@whaley.cn,zhang.dong@whaley.cn"
    msg = """
        <html><body>
         <p >%s</p>
         <h2 >Send by whaley_ops</h2>
    </body></html> """ % text
    send_mail(msg, mailto, subject)
    raise ("Get values error")


def check_data(data):
    for line in data:
        date, values01, values02, values03 = line
        if not _check_data(values01) or not _check_data(values02) or not _check_data(values03):
            text = "Get values error ,Values was :\t   %s,%s,%s,%s\n" % (date, values01, values02, values03)
            send_alter_mail(text)
    return True


def _check_data(num):
    if num:
        if int(num) > 1000:
            return True
    else:
        return False


def get_html_msg(file):
    with open(file, 'r') as f:
        data = f.read().split('\n')

    head = """ <html>
    <body>
    """

    p1 = """<h4> %s: </h4>
    <table border="1">
    """ % "Report Daily"
    # body="""     <html><body><table align=left border=1 width=70% style=height:30%><tr> <img  width=70% src='data:image/png;base64,$b64'</img>     """
    body = """     <html><body><table align=left border=1 width=70% style=height:30%>    """

    for _list in data:
        if _list:
            body += """<tr>
                <td align="left">%s</td>
                <td align="left">%s</td>
                 <td align="left">%s</td>
                  <td align="left">%s</td>
                   <td align="left">%s</td>
                   <td align="left">%s</td>
                </tr>
              """ % (
            _list.split(',')[0], _list.split(',')[1], _list.split(',')[2], _list.split(',')[3], _list.split(',')[4],
            _list.split(',')[5])

    html = head + p1 + body + """
    </table>
    </body>
    </html>
    """
    return html


def get_date(day=0, strftime="%Y-%m-%d"):
    date = (datetime.date.today() - datetime.timedelta(days=day)).strftime(strftime)
    return date


class Cdn_Values():
    def __init__(self, data):
        self.ip = data.get("ip", None)
        self.user = data.get("user", None)
        self.passwd = data.get("passwd", None)
        self.db = data.get("db", None)

    def cdn_day_max(self, cdnid):
        # self.cdn_list=(6,2)
        # 高升的motetvid=6，ucloud=2
        sql_cnd_day_max = """select sum(B.traffic) as total from cdn
                           as A INNER JOIN cdn_data AS B on A.id = B.relation_id
                           WHERE B.time  between %d AND %d AND A.id in
                           (select id  from cdn where operator_id=%d and dtype=2)
                          group by B.tirme order by total desc limit 1;"""
        end_day = get_date(day=-1, strftime="%Y%m%d")
        end_day_int = int(end_day + '0000')
        begin_day = get_date(day=-2, strftime="%Y%m%d")
        begin_day_int = int(begin_day + '0000')
        sql = sql_cnd_day_max % (begin_day_int, end_day_int, int(cdnid))
        m = MysqlBase(ip=self.ip, user=self.user, passwd=self.passwd, databases=self.db)
        data = m.query(sql)
        return data

    def cdn_95(self, cdnid):
        sql_95 = "select sum(B.traffic) as total from cdn " \
                 " as A INNER JOIN cdn_data AS B on A.id = B.relation_id   " \
                 "WHERE B.time  between %d AND %d AND A.id in" \
                 " (select id  from cdn where operator_id=%d and dtype=2) " \
                 "group by B.tirme order by total desc ;"
        end_day = get_date(day=0, strftime="%Y%m%d")
        if end_day[-2:] == '01':
            end_day = get_date(day=-1, strftime="%Y%m%d")

        end_day_int = int(end_day + '0000')
        begin_day = end_day[:-2] + '01'
        begin_day_int = int(begin_day + '0000')
        sql = sql_95 % (begin_day_int, end_day_int, int(cdnid))
        m = MysqlBase(ip=self.ip, user=self.user, passwd=self.passwd, databases=self.db)
        data = m.query(sql)
        data_95 = int(len(data) * 0.95)
        # 取整
        return data[data_95]

    def cdn_bigdata_values(self, cdnname):
        end_day = get_date(day=-1, strftime="%Y-%m-%d")
        begin_day = get_date(day=-91, strftime="%Y-%m-%d")

        sql = """select  day ,sum(num) ,totalNum ,sum(num)/totalNum
                                  from medusa_video_playqos_playcode_source
                                  where source= '%s'  and videoSid='All' and
                                 day between %s AND %s and playcode=200 group by day ;""" % (
        cdnname, begin_day, end_day)

        m = MysqlBase(ip=self.ip, user=self.user, passwd=self.passwd, databases=self.db)
        data = m.query(sql)
        return data


def write_data_file(file, data):
    input = "Date,Newuser,Activeuser,Total,Active/Total,Newuser/Yesterday Total \n"
    for i in range(len(data) - 1):
        input += "%s,%s,%s,%s,%s,%s \n" % (str(data[i][0]), \
                                           str(data[i][1]), str(data[i][2]), str(data[i][3]), \
                                           str(round(data[i][2] / float(data[i][3]), 7)), \
                                           str(round(data[i][1] / float(data[i + 1][3]), 7)))

    #
    # for line in new_data:
    #     input+=",".join('%s' % id for id in line) + '\n'
    with open(file, 'w') as f:
        f.write(input)


def get_config(filename, values):
    cf = ConfigParser.SafeConfigParser()
    sections = values
    cf.read(filename)
    configDataSection = cf.sections()
    returnData = {}

    if sections in configDataSection:
        _list = cf.items(sections)
        for _key, _value in _list:
            returnData[_key] = _value
    else:
        print "[ERROR] %s is not in config files,PLS check it %s" % (sections, filename)
        msg_info = "===%s: Get info Failed!!===" % sections
        logMsg("get_config", msg_info, 2)
        raise "Values could`t found in config"

    return returnData


def get_data_bigdata(data, items):
    d_list = list()
    for i in len(range(items)):
        cdn = Cdn_Values(data)
        d_list.append(cdn.cdn_bigdata_values(item))


def get_data_hms(data):
    cdn = Cdn_Values(data)
    # 高升=6，ucloud=2
    values_day_max_gaoshen = cdn.cdn_day_max(6)
    values_95_gaoshen = cdn.cdn_95(6)
    values_day_max_ucloud = cdn.cdn_day_max(2)
    values_95_ucloud = cdn.cdn_95(2)


def main():
    config_files = sys.argv[1]
    parm = "common"
    config_common_data = get_config(config_files, parm)

    bigdata_data = get_config(config_files, 'cdn_bigdata')
    items = bigdata_data.get("select_item", None).split(",")
    cdn_bigdata = get_data_bigdata(bigdata_data, items)





    #
    # data=get_db_data(ip,user,passwd,databases)
    # if check_data(data):
    #     file= config_data.get["output_file",None]
    #     write_data_file(file,data)
    #
    #     if create_png_all(file,config_data.get["items",None].split(","),config_data.get["png",None]) :
    #         html=get_html_msg(file)
    #         emailto=config_data.get["emailto",None]
    #         #emailto = "peng.tao@whaley.cn"
    #         subject=config_data.get["mail_sub",None]
    #         send_mail(html,emailto,subject,is_img=True)
    #     else:
    #         text="Create Png file Failed"
    #         send_alter_mail(text)


if __name__ == "__main__":
    main()
