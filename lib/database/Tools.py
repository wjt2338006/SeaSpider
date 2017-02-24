from pymongo import MongoClient


def explain(str):
    con_list = str.split(".")
    return con_list[0],con_list[1],con_list[2]


def get_mongo_cursor(con_str, link='mongodb://localhost:27017/'):
    con, table, pid = explain(con_str)
    print(con,table,pid)
    client = MongoClient(link)
    db = client[con]
    collection = db[table]
    return collection

# def cache_connection():
#     cache = {}
#     def get(conector_str,link='mongodb://localhost:27017/'):
#         if link not in cache:
#             cache[link] = get_mongo_cursor(conector_str,link):
#         return cache[link]
#     return get

