import pymysql
import Common


class Mysql:
    def __init__(self):
        config = Common.loadConfig()['db']['mysql']
        self.conn = pymysql.connect(host=config['host'], port=config['port'], user=config['username'],
                                    password=str(config['password']),
                                    db=config['db'],charset="utf8mb4")

    def __del__(self):
        self.conn.close()

    def dbSetBatch(self, sql, values):
        """
        批量插入数据
        :param sql: sql语句
        :param values: 要插入的数据，建议是list
        :return:
        """
        cur = self.conn.cursor()
        cur.executemany(sql, values)
        self.conn.commit()

    def dbSelect(self,sql):
        """
        sql查询
        :param sql:
        :return:
        """
        self.conn.ping(reconnect=True)
        cur = self.conn.cursor()
        cur.execute(sql)
        ret = cur.fetchall()
        return ret



