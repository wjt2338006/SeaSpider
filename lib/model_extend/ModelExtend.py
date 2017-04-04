import re

from .ConnectionPool import ConnectionPool
from .Tools import explain

template_re = "\[%s\]"
re_field = re.compile(r"as(.*)")

select_list = ["field", "table", "join", "where", "order", "limit"]
re_dict_select = dict(zip(select_list, [re.compile(template_re % i) for i in select_list]))

add_list = ["field", "value", "table"]
re_dict_add = dict(zip(add_list, [re.compile(template_re % i) for i in add_list]))

update_list = ["table", "value", "where"]
re_dict_update = dict(zip(update_list, [re.compile(template_re % i) for i in update_list]))

del_list = ["table", "where"]
re_dict_del = dict(zip(del_list, [re.compile(template_re % i) for i in del_list]))


class ModelExtend:
    con = "db.col.pk"  # 连接名.集合.主键
    auto_commit = True

    def __init__(self, primary_id, connection=None):
        if connection:
            con_str = connection
        else:
            con_str = self.con

        self.pid = primary_id
        self.data = {}
        self.flush(con_str)

    def flush(self, con_str):
        con, table, pid = explain(con_str)
        limit = {pid: self.pid, "$first": True}
        self.data = self.get(limit, con_str)

    @classmethod
    def get(cls, limit={}, connection=None):
        if connection:
            con_str = connection
        else:
            con_str = cls.con

        con, table, pid = explain(con_str)
        connector = ConnectionPool.get_connection(con)
        cursor = connector.cursor()
        sql = _explain_query_mysql(limit, table, pid)

        key_list = _get_special_key(limit, cursor, table)
        if "$first" in limit and limit["$first"] is True:
            limit["$limit"] = 1
        print(sql)
        cursor.execute(sql)

        data = [dict(zip(key_list, i)) for i in cursor]
        if "$link" in limit:
            _link(data, limit["$link"], con)
        if "$map" in limit:

            data = [limit["$map"](x) for x in data]

        if "$first" in limit and limit["$first"] is True:
            new_dict = {}
            if data:
                new_dict = data[0]
            data = new_dict
        cursor.close()

        return data

    @classmethod
    def add(cls, data, connection=None):
        if connection:
            con_str = connection
        else:
            con_str = cls.con
        con, table, pid = explain(con_str)
        if not data: raise ("empty data")

        origin_sql = "INSERT INTO [table] ([field]) VALUES ([value]);"
        ready_data = {}
        ready_data["field"] = ",".join(map(lambda x: "`%s`" % str(x), data.keys()))
        ready_data["value"] = ",".join(map(lambda x: "'%s'" % str(x), data.values()))
        ready_data["table"] = table

        origin_sql = _sub_placeholder(origin_sql, re_dict_add, ready_data)

        connector = ConnectionPool.get_connection(con)
        cursor = connector.cursor()
        cursor.execute(origin_sql)
        if cls.auto_commit:
            connector.commit()

    @classmethod
    def addById(cls, data, connection=None):
        if connection:
            con_str = connection
        else:
            con_str = cls.con
        con, table, pid = explain(con_str)
        max_id = cls.get({"$field": ["max(%s) as max_id" % pid], "$first": True}, connection)["max_id"]
        if not max_id:
            max_id = 0
        data[pid] = max_id+1
        cls.add(data, connection)
        return data[pid]

    @classmethod
    def delete(cls, limit={}, connection=None):
        if connection:
            con_str = connection
        else:
            con_str = cls.con
        con, table, pid = explain(con_str)

        if not limit:
            raise Exception("delete all is very danger")

        origin_sql = "DELETE FROM [table] [where];"
        ready_data = {}
        ready_data["table"] = "`%s`" % table
        ready_data["where"] = ""
        ready_data["where"] = _handle_where(limit)

        origin_sql = _sub_placeholder(origin_sql, re_dict_del, ready_data)

        connector = ConnectionPool.get_connection(con)
        cursor = connector.cursor()
        cursor.execute(origin_sql)
        if cls.auto_commit:
            connector.commit()

    def update(self, data, limit={}, connection=None):
        if connection:
            con_str = connection
        else:
            con_str = self.con
        con, table, pid = explain(con_str)
        if not data: raise ("empty data")
        limit[pid] = self.pid

        origin_sql = "UPDATE [table] SET [value] [where];"
        ready_data = {}
        ready_data["table"] = "`%s`" % table
        ready_data["value"] = ",".join(["`%s`='%s'" % (k, v) for (k, v) in data.items()])
        ready_data["where"] = _handle_where(limit)

        origin_sql = _sub_placeholder(origin_sql, re_dict_update, ready_data)

        connector = ConnectionPool.get_connection(con)
        cursor = connector.cursor()
        cursor.execute(origin_sql)
        if self.auto_commit:
            connector.commit()


def _get_special_key(limit, cursor, table):
    if "$field" in limit:
        key_list = []
        for i in limit["$field"]:
            g = re_field.search(i)
            if g:
                key_list.append(g.group(1).strip())
            else:
                key_list.append(i.strip())
        return key_list
    else:
        cursor.execute('show columns from %s;' % table)
        key_list = [i[0] for i in cursor]
        return key_list


def _explain_query_mysql(limit, table, pid):
    """
    支持参数
    {
        '$field':['f1','f2','f3'...],
        '$and': [
                    ["a","=","aValue"],
                    ["b","=","bValue"],
                    {"$and":[["c","cValue"],......]}
                ],

        "$link": [["key", "product_id", "db.table.item_product"],[] .......]
        "$start":0,
        "$limit":0,
        "$order":"id",
        "$desc":true,
        "$join":["left","table","a","b"] / ["table","a","b"]

    }
    :param limit:
    """
    origin_sql = "select [field] from [table] [join] [where] [order] [limit];"
    insert_dict = {
        "field": "*",  # ok
        "table": None,  # ok
        "join": "",  # ok
        "where": "",  # ok
        "order": "",  # ok
        "limit": "",  # ok
    }

    if "$field" in limit and type(limit["$field"]) == type([]):
        insert_dict["field"] = ", ".join(map(str, limit["$field"]))

    insert_dict["where"] = _handle_where(limit)

    if "$start" in limit:
        start = str(limit["$start"])
        limit_num = ",200"
        if "$limit" in limit:
            limit_num = ","+str(limit["$limit"])
        insert_dict["limit"] = "limit %s %s" % (start, limit_num)
    else:
        if "$limit" in limit:
            limit_num = "limit %s" % str(limit["$limit"])
        else:
            limit_num = ""
        insert_dict["limit"] = limit_num


    order_by = pid
    desc = ""
    if "$order" in limit:
        order_by = str(limit["$order"])
    if "$desc" in limit and limit["$desc"] == True:
        desc = "desc"
    insert_dict["order"] = "order by %s %s" % (order_by, desc)

    if "$join" in limit:
        join_str = ""
        for i in limit["$join"]:
            if len(i) == 3:
                join_str += " join `%s` on `%s` = `%s` " % (i[0], i[1], i[2])
            else:
                join_str += " %s join `%s` on `%s` = `%s` " % (i[0], i[1], i[2], i[3])

        insert_dict["join"] = join_str

    insert_dict["table"] = table

    origin_sql = _sub_placeholder(origin_sql, re_dict_select, insert_dict)
    return origin_sql


def _handle_where(query_limit):
    def call(limit, opr, opr_key):
        str_sql = ""
        end = ""
        if len(limit[opr_key]) > 1:
            str_sql += "("
            end = ")"

        count = 0
        str_list = []
        for i in limit[opr_key]:

            if count > 0:
                str_list.append(opr)

            if type(i) == type({}):
                str_list.append(_handle_where(i))

            if type(i) == type([]):
                if len(i) == 2:
                    key = i[0]
                    symbol = "="
                    value = i[1]
                else:
                    key = i[0]
                    symbol = i[1]
                    value = i[2]
                if isinstance(value, list):
                    symbol = "in"
                    value_str = []
                    for j in range(len(value)):
                        tmp = "'%s'" % str(value[j])
                        value_str.append(tmp)

                    value = "(%s)" % (", ".join(value_str))
                else:
                    value = "'%s'" % value
                str_list.append("`%s` %s %s" % (key, symbol, str(value)))

            count += 1
        str_sql += ("".join(str_list))
        str_sql += end
        return str_sql

    where_field = [(k, v) for (k, v) in query_limit.items() if k[0] != "$" and v]
    if "$and" not in query_limit:
        query_limit["$and"] = []
    for i in where_field:
        query_limit["$and"].append([i[0], i[1]])

    if "$and" in query_limit:
        where_str = call(query_limit, " and ", "$and")
    elif "$or" in query_limit:
        where_str = call(query_limit, " or ", "$or")
    else:
        where_str = ""
    if where_str:
        where_str = "WHERE " + where_str
    return where_str


def _link(data, link, con):
    '''
    link =
    [
        ["sonKey","self","connetion.table.id",next_level_limit],
        [null,"self","table.id"] 嵌入式且使用父级别的链接
    ]
    :param link:
    :param connection:
    :return:
    '''
    foreigner_con = []
    for i in link:
        i_con = i[2].split(".")
        if len(i_con) == 2:
            connector = con
            table = i_con[0]
            fid = i_con[1]
        else:
            connector = i_con[0]
            table = i_con[1]
            fid = i_con[2]
        f_con = "%s.%s.%s" % (connector, table, fid)
        if len(i) < 4:
            i.append({})
        # [connection,sonKey,selfKey,foreignKey,limit,data]
        foreigner_con.append([f_con, i[0], i[1], fid, i[3], []])

    # 将符合条件数据存入
    for i in data:
        for j in foreigner_con:
            j[5].append(i[j[2]])

    # 存入where条件
    for i in foreigner_con:
        son_limit = i[4]
        if "$and" not in son_limit:
            son_limit["$and"] = []
        if i[0] is None:
            son_limit["$first"] = True
        where_list = list(set([j for j in i[5]]))
        if where_list:
            son_limit["$and"].append([i[3], where_list])
            i[5] = []
            son_data = ModelExtend.get(i[4], i[0])
            if type(son_data) is type({}):
                i[5] = [son_data]
            else:
                i[5] = son_data

    # 重新配到数据
    for i in data:
        for j in foreigner_con:
            # 针对单条多条，预先分配空间
            if j[1] is not None:
                if "$first" in j[4] and j[4]["$first"] is True:
                    i[j[1]] = {}
                else:
                    i[j[1]] = []
            # 将数据装入
            for k in j[5]:
                if k[j[3]] == i[j[2]]:
                    if j[1] is None:
                        i.update(k)
                    else:
                        if "$first" in j[4] and j[4]["$first"] is True:
                            i[j[1]] = k
                        else:
                            i[j[1]].append(k)


def _sub_placeholder(origin_sql, re_dict, data):
    for v in re_dict.items():
        k = v[0]
        re_tmp = v[1]
        origin_sql = re_tmp.sub(data[k], origin_sql)
    return origin_sql


if __name__ == "__main__":
    def test_select():
        config = [
            {
                "name": "db",
                "host": "127.0.0.1",
                "port": 3306,
                "db": "tff_tmall",
                "num": "auto",
                "type": "mysql",
                "username": "root",
                "password": "123",
                "charset": "utf8",

            }
        ]
        ConnectionPool.load_config(config)
        con = ConnectionPool.get_connection("db")
        limit = {"$field": ["tmall_ticket_id as id"],
                 "$and": [["template_priority", 34], ["tmall_ticket_id", [1, 3, 4, 9]]],
                 "$link": [[]]}

        limit = \
            {
                "$link":
                    [
                        ["group", "admin_group", "permission_group.group_id",
                         {
                             "$link":
                                 [
                                     ["permit", "group_id", "permission_group_re_power.re_group_id"]
                                 ]
                         }
                         ]
                    ]
            }
        i = ModelExtend.get(limit, "db.tmall_admin.admin_id")
        print(i)


    def add():
        data = {
            "permission_name": 1,
            "permission_group": 1
        }
        ModelExtend.add(data, "basic.permission.permission_id")
        print("aa")


    def update():
        data = {
            "permission_name": 1,
            "permission_group": 1
        }
        m = ModelExtend(3, "basic.permission.permission_id")

        m.update(data, connection="basic.permission.permission_id")


    def delete():
        m = ModelExtend(3, "basic.permission.permission_id")
        m.delete(connection="basic.permission.permission_id")


    delete()
'''
todo
父级别数据为空，自己别where in 空了
'''
