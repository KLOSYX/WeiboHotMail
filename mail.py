# smtplib 用于邮件的发信动作
import sql
import smtplib
from email.mime.text import MIMEText
# email 用于构建邮件内容
from email.header import Header
import time
import log
import threading

class Mail(threading.Thread):
    def __init__(self, config, sleep_time = 60, top = 5, send_time = '08', thread_name = 'send_mail'):
        super(Mail, self).__init__(name=thread_name)
        self.day = "0000-00-00"
        self.sleep_time = sleep_time
        self.top = top
        self.send_time = send_time
        self._terminate = False
        self._config = config
        
    def send_mail(self, msg):
        # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
        date = time.strftime('%Y-%m-%d', time.localtime())
        msg = MIMEText(msg, 'HTML', 'utf-8')

        # 邮件头信息
        msg['From'] = Header(self._config.from_addr)
        msg['To'] = Header(self._config.to_addr)
        msg['Subject'] = Header(date + ' 今日微博热搜推送')

        # 开启发信服务，这里使用的是加密传输
        server = smtplib.SMTP_SSL(host = self._config.smtp_server)
        server.connect(self._config.smtp_server, 465)
        # 登录发信邮箱
        server.login(self._config.from_addr, self._config.password)
        # 发送邮件
        server.sendmail(self._config.from_addr, self._config.to_addr, msg.as_string())
        # 关闭服务器
    
    def run(self):
        while(True):
            try:
                today = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400)) # yesterday
                now = time.strftime('%H', time.localtime())
                if(today != self.day and now == self.send_time):
                # if(True):
                    op = sql.Operation(db=self._config.db, user=self._config.user, passwd=self._config.passwd)
                    res = op.get_top_hot(today, self.top)
                    del op
                    if res:
                        msg = self.msg_format(res)
                        print(msg)
                        self.send_mail(msg)
                        print('邮件发送成功')
                    self.day = today
                log.log(f'mail: now sleeping for {self.sleep_time}')
                time.sleep(self.sleep_time)
                
            except KeyboardInterrupt:
                return
            
            except Exception as ex:
                log.logging.error(ex)
                exit(1)
                
    def msg_format(self, data):
        date = time.strftime('%Y-%m-%d %H:%M', time.localtime())
        msg = '<h1>早上好，这里是今日微博热搜</h1>\n<ol>'
        for i in data:
            msg += '<li>'
            msg +=  f"""<p style=color:red>热度：{str(i['hot'])} </p>"""
            msg += f"""<a href = '{str(i['url'])}'>{str(i['descr'])}</a>"""
            msg += '</li>\n'
        msg += f'</ol><hr><p style=color:gray>{date} 消息结束</p>'
        return msg