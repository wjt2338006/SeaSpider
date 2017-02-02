import json
import traceback

import requests
from bs4 import BeautifulSoup


def parse(data, type, worker_obj):
    print("我调用了jd parse")
    # if type == TYPE_LIST_PAGE:
    #     parse_list_page(data,worker_obj)
    # if type == TYPE_SINGLE_GOODS:
    #     parse_single_goods(data,worker_obj)


def parse_list_page(data,worker_obj):
    data = BeautifulSoup(data, "lxml")
    result_list = data.find_all(name="li", class_="gl-item")
    print(data)
    for k in range(0, len(result_list)):
        i = result_list[k]
        yield (str(i), TYPE_SINGLE_GOODS)


def parse_single_goods(html_data,worker_obj):
    html = BeautifulSoup(html_data, 'html5lib').find(name="li")

    data = {}
    data["jd_id"] = ""
    data["name"] = ""
    try:
        name_div = html.find(name="div", class_="p-name")
        data["name"] = name_div.a.em.get_text()

        data["price"] = html.find(name="div", class_="p-price").strong.i.get_text()
        data["detail_url"] = name_div.a["href"]
        data["jd_id"] = html["data-spu"]
        data["seller_name"] = explain_shop(html, data)
        # data["order"] = index

    except Exception as e:
        print('解析错误'+str(e))
        traceback.print_exc(e)



def explain_shop(div,data):
    seller_name = ""
    try:
        seller_name = div.find(name="div", class_="p-shop").span.a["title"]
        return str(seller_name)
    except Exception as e:
        print("seller_name 无法找到")
        seller_name = ""
        return str(seller_name)

TYPE_LIST_PAGE = 1
TYPE_SINGLE_GOODS = 2


def push_to_jd(data):
    url = "http://127.0.0.12/api/input"
    sendData = {"param": {
        'api': "pushJdData"
    }}
    sendData["param"]["args"] = {
        'data_name': data["name"],
        'data_price': data["price"],
        'data_detail_url': data["detail_url"],
        'data_jd_id': data["jd_id"],
        'data_seller_name': data["seller_name"],
        # 'data_order': data["order"]
    }

    r = requests.post(url, json=sendData)
    result = json.loads(r.text)

    if result["status"] == 200:
        print('ok,i get some page')
        pass
    else:
        print('server error')