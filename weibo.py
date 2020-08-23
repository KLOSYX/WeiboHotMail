#!/usr/bin/python

import requests
import re
import time
import log
import sql
import hashlib
import threading
import numpy as np
import savefile
import config


url = 'https://s.weibo.com/top/summary'

config = config.config()

db = config.db
user = config.user
passwd = config.passwd


class Weibo(threading.Thread):

    def __init__(self, thread_name='spider', fresh_time=60):
        super(Weibo, self).__init__(name=thread_name)
        self._data = {}
        # self._save_time = save_time
        self._infos = ('rank', 'url', 'description', 'index',
                       'tag', 'time', 'last_time')    # 请勿修改此项
        # self.filename = 'hot_topic.csv'
        self.class_name = 'weibo'   # 文件夹分类名
        self._fresh_time = fresh_time   # 抓取间隔
        self._save_time = '99'  # 初始化储存时间

    def _binary_fall_back(self, init=0):
        i = init
        while True:
            yield 2 ** i
            i += 1

    def get_post(self, time_out=15):
        '''
        抓取网页
        返回text部分
        '''
        i = 0
        b = self._binary_fall_back()
        fall_back = []
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.66'}
        while True:
            while i < 3:
                try:
                    time.sleep(10. * np.random.rand())
                    respon = requests.get(
                        url, timeout=time_out, headers=headers)
                    if respon.status_code != 200:
                        respon.raise_for_status()
                    return respon.text
                except requests.exceptions.RequestException:
                    i += 1
            # if i is 3:
            fall_back.append(next(b))
            sleep_time = max(60. * \
                fall_back[np.random.random_integers(0, len(fall_back) - 1)], 3600.)
            log.log(
                f'Retries all failed, now falling back for {sleep_time}...')
            time.sleep(sleep_time)
            i = 0
            # exit(1)

    def get_list(self, text):
        '''
        获取整个原始热搜列表
        '''
        assert text is not None, 'Get post before search'
        rstring = r'<tbody>(.*)</tbody>'  # 此处为贪心匹配
        pattern = re.compile(rstring, re.S | re.M)
        res = re.search(pattern, text)
        return res.group(0)

    def get_each(self, h_list):
        '''
        获取单独的每条热搜组成的列表
        '''
        assert h_list is not None, 'Top list is none'
        rstring = r'<tr class="">(.*?)</tr>'  # 非贪心匹配
        pattern = re.compile(rstring, re.S | re.M)
        res = re.findall(pattern, h_list)
        return res

    def process_each(self, top_list):
        '''
        返回有效数据
        group:
        1. rank
        2. url
        3. description
        4. index
        5. tag(optional)
        '''
        rstring = r'<td class="td-01 ranktop">(.*?)</td>.*?<a href="(.*?)" target="_blank">(.*?)</a>.*?<span>(.*?)</span>.*?<td class="td-03"><i class=".*?">(.*?)</i></td>'
        pattern = re.compile(rstring, re.S | re.M)
        all_group = re.search(pattern, top_list)
        res = []
        if all_group is not None:
            for item in all_group.groups():
                res.append(item)
            return res
        return None

    def format_each(self, single_list):
        '''
        返回格式化的数据
        '''
        format_dict = {}
        # if len(single_list) == 4:  # if tag not exsit
        #     all_info = self._infos[:-1]
        # else:
        all_info = self._infos
        for key, element in zip(all_info, single_list):
            format_dict[key] = element
        format_dict['url'] = 'https://s.weibo.com' + \
            format_dict['url']  # add prefix
        format_dict['time'] = self._local_time()    # add time tag
        # add last modified time tag
        format_dict['last_time'] = format_dict['time']
        return format_dict

    def _save_data(self, element):
        '''
        在_data中储存单条信息
        '''
        m2 = hashlib.md5()
        if element is not None:
            formatted = self.format_each(element)
            m2.update(formatted['description'].encode('utf8'))
            hash_value = m2.hexdigest()
            if hash_value in self._data:
                # 更新last_time
                self._data[hash_value]['last_time'] = self._local_time()
                if int(formatted['rank']) < int(self._data[hash_value]['rank']):  # top rank
                    self._data[hash_value]['rank'] = formatted['rank']
                if int(formatted['index']) > int(self._data[hash_value]['index']):  # highest index
                    self._data[hash_value]['index'] > formatted['index']
            else:
                self._data[hash_value] = formatted  # 将discription的哈希值作为标记
        return

    def _local_time(self, H=True, M=True):
        assert isinstance(H, bool) and isinstance(
            M, bool), 'H and M must be bool value'
        assert H or M, 'H or M must be set to True'
        if H == True and M == True:
            time_string = '%H:%M'
        elif H == True and M == False:
            time_string = '%H'
        else:
            time_string = '%M'
        return time.strftime(time_string, time.localtime())

    def _get_and_process(self):
        h_list = self.get_list(self.get_post())
        top_list = self.get_each(h_list)
        element = []
        for item in top_list:  # 循环热搜
            if item is not None:
                formatted = self.process_each(item)
                if formatted is not None:
                    element.append(formatted)
        return element

    def run(self):
        try:
            # self.read()
            self._save_time = self._local_time(M=False)  # 初始化保存时间
            while True:
                log.log('getting data now...')
                elements = self._get_and_process()
                log.log('data got successfully')
                for e in elements:
                    self._save_data(e)
                # self.save()
                log.log('data saved to memory')
                self.save_to_database()
                if self._check_point():  # 检查是否转点，如果转点，则更换文件保存并移除长时间未更新的条目
                    self._remove_old()
                log.log(f'now sleeping for time {self._fresh_time}')
                time.sleep(self._fresh_time)

        except KeyboardInterrupt:
            # self.save()
            self.save_to_database()
            return

    def _remove_old(self):
        for key in list(self._data.keys()):
            now = time.time()
            last = self._mktime(self._data[key]['last_time'])
            if now - last > 600:    # remove for an hour
                log.log('removed old entry: ' + str(key))
                self._data.pop(key)
            else:
                pass

    def _mktime(self, s):
        '''
        input string format: %H:%M
        output: timestrap(secs)
        '''
        return time.mktime(time.strptime(time.strftime('%Y%m%d', time.localtime()) + s, '%Y%m%d%H:%M'))

    def _check_point(self):
        res = False
        now = self._local_time(M=False)
        if now != self._save_time:
            self._save_time = now
            res = True
        return res

    def save(self):
        '''
        储存到文件
        '''
        filename = self._save_time + '.csv'
        path = savefile.chek_folder(self.class_name)
        with open(path + '/' + filename, 'w', encoding='utf-8') as of:
            for key in self._data:
                of.write(str(key) + ', ')
                for key2 in self._infos[:-1]:
                    of.write(str(self._data[key][key2]) + ', ')
                    # log.log(str(self._data[key][key2]) + '\n')
                of.write(str(self._data[key][self._infos[-1]]) + '\n')
                # log.log(str(self._data[key][self._infos[-1]]) + '\n')
        log.log('file saved: ' + filename)

    def save_to_database(self):
        '''
        储存到数据库
        '''
        op = sql.Operation(db=db, user=user,
                           passwd=passwd)
        date = time.strftime('%Y-%m-%d', time.localtime())
        for key in self._data:  # all hash value
            if not op.check_it(key):  # first store
                data = '\'' + str(key) + '\', '
                for key2 in self._infos[:-2]:
                    data += '\'' + self._data[key][key2] + '\', '
                data += '\'' + date + ' ' + \
                    self._data[key]['time'] + ':00\'' + ', \'' + \
                        date + ' ' + self._data[key]['last_time'] + ':00\''
                op.insert_to_database(data)
            else:  # not the first store
                las = date + ' ' + self._data[key]['last_time'] + ':00'
                rank = self._data[key]['rank']
                index = self._data[key]['index']
                data = (rank, index, las)
                op.update(key, data)
        del op
        log.log('data saved')
