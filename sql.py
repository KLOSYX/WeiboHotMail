import pymysql

# database setting
'''
CREATE TABLE `weibo` (
  `hash` char(32) NOT NULL,
  `rank` tinyint(11) NOT NULL,
  `url` text NOT NULL,
  `descr` text NOT NULL,
  `hot` bigint(11) NOT NULL,
  `tag` varchar(10) DEFAULT NULL,
  `cre` datetime NOT NULL,
  `las` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
'''


class DB():
    def __init__(self, host='localhost', port=3306, db='', user='root', passwd='root', charset='utf8'):
        # 建立连接
        self.conn = pymysql.connect(
            host=host, port=port, db=db, user=user, passwd=passwd, charset=charset)
        # 创建游标，操作设置为字典类型
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __enter__(self):
        # 返回游标
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交数据库并执行
        self.conn.commit()
        # 关闭游标
        self.cur.close()
        # 关闭数据库连接
        self.conn.close()


class Operation(object):
    def __init__(self, host='localhost', port=3306, db='', user='root', passwd='root', charset='utf8'):
        self.conn = pymysql.connect(
            host=host, port=port, db=db, user=user, passwd=passwd, charset=charset)
        self.db = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def check_it(self, hash):
        sql = f"SELECT * FROM weibo WHERE hash = '{hash}'"
        try:
            self.db.execute(sql)
            res = self.db.fetchone()
        except Exception:
            print(Exception)
            exit(1)
        if(res):
            return True
        return False

    def insert_to_database(self, data):
        sql = f"""INSERT INTO weibo
        (hash, rank, url, descr, hot, tag, cre, las)
        VALUES ({data})"""
        try:
            self.db.execute(sql)
        except Exception as ex:
            print(ex)
            exit(1)

    def update(self, hash, data):
        '''
        data(tuple): (rank, index, las)
        '''
        sql = f"""UPDATE weibo SET
        rank = '{data[0]}', hot = '{data[1]}', las = '{data[2]}'
        WHERE hash = '{hash}'
        """
        try:
            self.db.execute(sql)
        except Exception as ex:
            print(ex)
            exit(1)

    def get_top_hot(self, date, top=3):
        sql = f"""SELECT hot, descr, url FROM weibo 
        WHERE DATE_FORMAT(cre, '%Y-%m-%d') = '{date}' 
        ORDER BY hot DESC;"""
        try:
            self.db.execute(sql)
            all_res = self.db.fetchall()
            if (top > len(all_res)):
                top = len(all_res)
            res = all_res[0:top]
        except Exception as ex:
            print(ex)
            exit(1)
        return res

    def __del__(self):
        # 提交数据库并执行
        self.conn.commit()
        # 关闭游标
        self.db.close()
        # 关闭数据库连接
        self.conn.close()

# def main():
#     data = """
#     '7', 'https://baidu.comcc/sdlkoicu', '你好世界', '27789', '新', '20141231050505', '20201231050507'
#     """
#     #insert_to_database(data)
#     update('67789602', '20201231050522')

# if __name__ == "__main__":
#     main()
