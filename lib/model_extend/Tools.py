import re
from pymongo import MongoClient


def explain(str):
    con_list = str.split(".")
    return con_list[0], con_list[1], con_list[2]


def get_mongo_cursor(con_str, link='mongodb://localhost:27017/'):
    con, table, pid = explain(con_str)
    client = MongoClient(link)
    db = client[con]
    collection = db[table]
    return collection


def select_page_filter(limit):
    num = 200
    start = 0
    if "start" in limit:
        start = limit["start"]
        del limit["start"]
    if "num" in limit:
        num = limit["num"]
        del limit["num"]
    need_del = [k for k, v in limit.items() if v == ""]
    for i in need_del: del limit[i]
    return limit, start, num


filter_regex = {
    "number": lambda data, x: str(data[x]).isdigit(),
    "required": lambda data, x:True if x in data and data[x] else False,
    "word": re.compile(r"\W"),
    "chinese": re.compile(r""),
    "url": re.compile(r"(http://|https://)*[\w]+\.[\w]+\.[\w]+.+]")
}
filter_message = {
    "number": "%s 必须为数字",
    "required": "%s 必须存在",
    "word": "%s 必须为正常文本",
    "chinese": "%s 必须为中文",
    "url": "%s 必须为URL"
}
re_tem = re.compile(r".*")


# 需要测试
def check_input(check, input_data):
    def _check(filter_opr,input_data,k):
        r = False
        if k not in input_data:
            raise Exception("no this field %s"%k)
        if type(filter_opr) == type(re_tem):
            if filter_opr.search(input_data[k]):
                r = True
        elif type(filter_opr) == type(check_input):
            r = filter_opr(input_data, k)
        return r

    error_list = []
    return_data = {}
    for k,v in check.items():
        check_str = check[k]
        #过滤
        if not check_str:
            if k in input_data:
                return_data[k] = v
            continue
        #检查
        tmp_error = []
        r= False
        for i in check_str.split("|"):
            if i in filter_regex:
                regex = filter_regex[i]
                if _check(regex,input_data,k):
                    r = True
                    break
                else:
                    tmp_error.append([k, filter_message[i]%k])
            else:
                raise Exception("no this regex")
        if not r:
            error_list += tmp_error

    #报错
    if error_list:
        raise InputValidationException(error_list)


def convert_db_config_django(django_obj):
    pass


class InputValidationException(Exception):
    def __init__(self, message=[]):
        self.message = message


if __name__ == "__main__":
    data = {
        "name": "saca",
        "age": 16,
        "small": "sadas",
        "gg": "xs",
        "xsa":""
    }
    check_input({"name": "required", "age": "number", "small": None,"xsa":"required"}, data)
    print(data)
    pass
