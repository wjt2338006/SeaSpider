class ConnectionPool:
    connection_pool = {}
    @classmethod
    def load_config(cls, config):
        """
        装入配置，在初始化程序的时候就调用
        :param config:
        """
        cls.config = config
        cls.connection_pool = {}
        for con in config:
            if type(con["num"]) == "int":
                cls.connection_pool[con["name"]] = [Connection(con) for j in range(con["num"])]
            elif con["num"] == "auto":
                cls.connection_pool[con["name"]] = [Connection(con)]

    @classmethod
    def get_connection(cls, name,read_only=False):

        """
        获取连接，接受者应该使用with
        :rtype: object
        """
        if name not in cls.connection_pool:
            raise Exception("error connection,not find")

        rand_position = 0
        con = cls.connection_pool[name][rand_position]
        return con.connector


class Connection():
    def __init__(self, config):
        self.host = config["host"]
        self.db = config["db"]
        self.name = config["name"]
        self.type = config["type"]
        self.username = config["username"]
        self.password = config["password"]
        self.charset = config["charset"]
        self.port = config["port"]
        self.connector = None
        self.locked = False
        self.connect()

    def connect(self):
        def mysql_connect():
            config = {'host': self.host,  # 默认127.0.0.1
                      'user': self.username,
                      'password': self.password,
                      'port': self.port,  # 默认即为3306
                      'database': self.db,
                      'charset': self.charset  # 默认即为utf8
                      }
            import mysql.connector
            connector = mysql.connector.connect(**config)
            return connector

        def mongodb_connect():
            return {}

        call_dict = {
            "mongodb": mongodb_connect,
            "mysql": mysql_connect
        }

        self.connector = call_dict[self.type]()

    def disconnect(self):
        def mysql():
            pass

        def mongodb():
            pass

        call_dict = {
            "mongodb": mongodb,
            "mysql": mysql
        }
        call_dict[self.type]()

        # def is_locked(self):
        #     return self.locked
        #
        # def lock(self):
        #     while True:
        #         if not self.locked:
        #             self.locked = True
        #             break
        #         else:
        #             continue
        #
        # def unlock(self):
        #     if self.locked:
        #         self.locked = False
        #     else:
        #         raise Exception("lock is unlocked")
        #
        # def __enter__(self):
        #     self.lock()
        #
        # def __exit__(self, exc_type, exc_value, exc_tb):
        #     self.unlock()
