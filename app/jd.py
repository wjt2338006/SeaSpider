#-*- coding:utf-8 -*-
import json
import traceback
import urllib
from time import sleep, time

import logging

import requests
import sys
from bs4 import BeautifulSoup

from lib.Log import Log
from lib.database.Tools import get_mongo_cursor
from lib.exception.Exception import ParseError

jd_data_store = get_mongo_cursor("spider.jd._id")

"""
{
    "url":需要被爬取的url
    "total":总页数
    "index":关键字
}
"""
page_total = {}


def handle(download, get_url_data, log):
    try:
        url = get_url_data["url"]

        download.driver.get(url)

        total_page = 2  # get_url_data["total"]
        index_key = get_url_data["index"]
        # print(url)
        for i in range(0, int(total_page)):
            print("当前第" + str(i + 1) + "页")
            if i > 0:
                download.driver.find_element_by_class_name('pn-next').click()
                sleep(4)
                download.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                sleep(1)
            else:
                download.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                sleep(2)
            data = download.driver.page_source
            # print(str(data))
            yield [str(data), TYPE_LIST_PAGE, {"page": i + 1, "index_key": index_key}]
    except Exception as e:
        error = "handle error:" + traceback.format_exc()
        # logging.info(error)
        print(error)
        return False


# 这里获得的obj就是handle返回的那个
def parse(recv_obj, log, final_queue):
    print("解析结果", recv_obj)
    data = recv_obj[0]
    data_type = recv_obj[1]
    other = recv_obj[2]
    if data_type == TYPE_LIST_PAGE or data_type is None:
        now_index_key = None
        if other["index_key"] not in page_total:
            page_total[other["index_key"]] = {}

        now_index_key = page_total[other["index_key"]]

        data = BeautifulSoup(recv_obj[0], "lxml")
        result_list = data.find_all(name="li", class_="gl-item")
        print("共有块元素" + str(len(result_list)))

        # 注意加入了这个功能以后要确保拿到的页码数据有序,同时目前代码没有保证线程安全
        if other["page"] == 1:
            true_index = 0  # 记录有效的商品,如果是第一页的话，设置为0
        else:
            try:
                true_index = now_index_key["page_" + str(other["page"] - 1)]  # 如果是后面的页数的话 设定为前面页商品之和
            except IndexError as e:
                print("前一页数据还没准备好")
                raise e

        for k in range(0, len(result_list)):
            i = result_list[k]
            # li = i.find(name="li")
            # print(li)
            if "data-type" in i and i["data-type"] == "activity":
                continue
            true_index += 1
            # print(true_index)
            yield (str(i), TYPE_SINGLE_GOODS, dict(other, **{"page_offset": true_index, "all_offset": true_index}))
        now_index_key["page_" + str(other["page"])] = true_index

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

            data["data_price"] = explain_price(html)
            data["data_detail_url"] = name_div.a["href"]
            data["data_jd_id"] = html["data-sku"]
            data["data_seller_name"] = explain_shop(html)
            data["data_page_offset"] = other["page_offset"]
            data["data_page_number"] = other["page"]
            data["data_index_key"] = other["index_key"]
            data["data_order"] = other["all_offset"]
            # print(data)  # 已经提取到了数据
            push_to_jd(data, final_queue)
            return None
        except Exception as e:
            error = "result  error:" + traceback.format_exc()
            # logging.info(error)
            print(error)

            raise ParseError("Parse Error " + error)


def explain_shop(div):
    seller_name = "自营"
    try:
        seller_name = div.find(name="div", class_="p-shop").span.a["title"]
        return str(seller_name)
    except Exception as e:
        return str(seller_name)


def explain_price(div):
    p = None
    try:
        p = div.find(name="div", class_="p-price").strong.i.get_text()
    except e:
        p = None
    finally:
        return p


TYPE_LIST_PAGE = 1
TYPE_SINGLE_GOODS = 2


def push_to_jd(data, final_queue):
    data["spider_time"] = time()
    data = json.dumps(data)
    final_queue.produce(data.encode())
    # isset = jd_data_store.find_one({"data_jd_id":data["data_jd_id"]})
    # if isset:
    #     jd_data_store.update({"data_jd_id":data["data_jd_id"]},data)
    # else:
    #     r = jd_data_store.insert(data)

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
