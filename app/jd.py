import json
import traceback
from time import sleep, time

import logging
import requests
import sys
from bs4 import BeautifulSoup

# 单例一个MongoDB链接
from pymongo import MongoClient

from lib.Log import Log
from lib.database.Tools import get_mongo_cursor

jd_data_store = get_mongo_cursor("spider.jd._id")

"""
{
    "url":需要被爬取的url
    "total":总页数
    "index":关键字
}
"""


def handle(download, get_url_data, log):
    try:
        download.driver.get(get_url_data["url"])
        total_page = get_url_data["total"]
        index_key = get_url_data["index"]
        for i in range(0, int(total_page)):
            if i != 0:
                download.dirver.find_element_by_class_name('pn-next').click()
                sleep(3)
            data = download.driver.page_source
            print(str(data))
            yield [str(data), TYPE_LIST_PAGE, {"page": i, "index_key": index_key}]
    except Exception as e:
        traceback.format_exc()
        return False


# 这里获得的obj就是handle返回的那个
def parse(recv_obj, log):
    print("解析消息",recv_obj)
    data = recv_obj[0]
    data_type = recv_obj[1]
    other = recv_obj[2]
    if data_type == TYPE_LIST_PAGE or data_type is None:
        data = BeautifulSoup(recv_obj[0], "lxml")
        result_list = data.find_all(name="li", class_="gl-item")
        for k in range(0, len(result_list)):
            i = result_list[k]
            yield (str(i), TYPE_SINGLE_GOODS, dict(other, **{"page_offset": k}))

    if data_type == TYPE_SINGLE_GOODS:
        html = BeautifulSoup(data, 'lxml').find(name="li")

        data = {
            'data_name': "",
            'data_price': "",
            'data_detail_url': "",
            'data_jd_id': "",
            'data_seller_name': "",
            'data_order': ""
        }
        try:
            name_div = html.find(name="div", class_="p-name")
            data["data_name"] = name_div.a.em.get_text()

            data["data_price"] = html.find(name="div", class_="p-price").strong.i.get_text()
            data["data_detail_url"] = name_div.a["href"]
            data["data_jd_id"] = html["data-spu"]
            data["data_seller_name"] = explain_shop(html, data)
            data["data_page_offset"] = other["page_offset"]
            data["data_page_number"] = other["page"]
            data["data_index_key"] = other["index_key"]
            print(data)  # 已经提取到了数据
            push_to_jd(data)
            return None
        except Exception as e:
            print(traceback.format_exc())


def explain_shop(div, data):
    seller_name = "自营"
    try:
        seller_name = div.find(name="div", class_="p-shop").span.a["title"]
        return str(seller_name)
    except Exception as e:
        return str(seller_name)


TYPE_LIST_PAGE = 1
TYPE_SINGLE_GOODS = 2


def push_to_jd(data):
    r = jd_data_store.insert(data)

    # str = data["name"]
    #
    # with open("/home/jedi/output","w+") as f:
    #     f.write(str)
    # url = "http://laravel_template.com/api/input"
    # sendData = {"param": {
    #     'api': "pushJdData"
    # }}
    # sendData["param"]["args"] = {
    #     'data_name': data["name"],
    #     'data_price': data["price"],
    #     'data_detail_url': data["detail_url"],
    #     'data_jd_id': data["jd_id"],
    #     'data_seller_name': data["seller_name"],
    #     # 'data_order': data["order"]
    # }
    #
    # r = requests.post(url, json=sendData)
    # result = json.loads(r.text)
    #
    # if result["status"] == 200:
    #     print('ok,i get some page')
    #     sleep(1)
    #     pass
    # else:
    #     print('server error')


#
# def after_get(dirver, worker):
#     n = 0
#     while n < 10:
#         print('完成后点击了下一页')
#         dirver.find_element_by_class_name('pn-next').click()
#         sleep(5)
#         worker.push_result(str(dirver.page_source), None)
#         print("推入了结果")
#         n += 1
if __name__ == "__main__":
    try:
        push_to_jd({
            'data_name': "测试联通的商品",
            'data_price': "19.99",
            'data_detail_url': "详情页面的url",
            'data_jd_id': "jd 商品id",
            'data_seller_name': "超级无敌大卖场",
            'data_order': "16"
        })
    except Exception as e:
        error = traceback.format_exc()

        # traceback.print_exception(e,"err",None)

