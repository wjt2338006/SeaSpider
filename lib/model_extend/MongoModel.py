import time

from bson import ObjectId
from pymongo import MongoClient

from Tools import get_mongo_cursor, select_page_filter


class MongoModel(object):
    host = "mongodb://localhost:27017/"
    con = "db.col.pk"

    soft_del_field = "is_del"
    soft_del = False

    def __init__(self, id):
        self.connector = get_mongo_cursor(self.__class__.con, self.__class__.host)
        self.id = id
        self.data = {}

    def flush(self):
        self.data = self.connector.find_one({"_id": ObjectId(id)})
        if self.data:
            return self.data
        else:
            raise NotFindException

    """
        获取数据
    """

    @classmethod
    def get(cls, limit={}):
        limit, start, num = select_page_filter(limit)
        con = get_mongo_cursor(cls.con, cls.host)
        r = con.find(limit)
        if num: r.limit(int(num))
        if start: r.skip(int(start))
        for i in r:
            i["_id"] = str(i["_id"])
            i["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i["created_at"]))
            i["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i["updated_at"]))
            yield i

    @classmethod
    def add(cls, data):
        con = get_mongo_cursor(cls.con, cls.host)
        # print(con)

        data["created_at"] = time.time()
        data["updated_at"] = time.time()
        if cls.soft_del:
            data[cls.soft_del_field] = False
        r = con.insert(data)
        return cls(r)

    def update(self, data):
        data["updated_at"] = time.time()
        return self.connector.update({"_id": ObjectId(self.id)}, {"$set": data})

    def delete(self):
        if self.__class__.soft_del:
            self.connector.update({"_id": ObjectId(self.id)}, {"$set": {self.__class__.soft_del_field: True}})
        else:
            return self.connector.delete_one({"_id": ObjectId(self.id)})


class NotFindException(Exception):
    pass






