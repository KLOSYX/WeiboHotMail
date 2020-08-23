#!/usr/bin/python

class Config(object):
    def __init__(self):
        # 用于构建邮件头
        # 发信方的信息：发信邮箱，QQ 邮箱授权码
        self.from_addr = 'xxxxx@qq.com'
        self.password = 'xxxxx'
        # 收信方邮箱
        self.to_addr = 'xxxxx@outlook.com'
        # 发信服务器
        self.smtp_server = 'smtp.qq.com'

        # database setting
        self.db = 'weibo'
        self.user = 'weibo'
        self.passwd = 'weibo'