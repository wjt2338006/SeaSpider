import json
from time import sleep, time

import requests
from bs4 import BeautifulSoup


def handle(download, get_url_data, log):
    try:

        for i in range(0,1):
            print(download)

            download.driver.get(get_url_data["url"])
            data = download.driver.page_source
            print(str(data))
            yield [str(data), TYPE_LIST_PAGE, {"page": 1}]
    except Exception as e:
        print(e)
        return False

# 这里获得的obj就是handle返回的那个
def parse(recv_obj,log):
    data = recv_obj[0]
    if recv_obj[1] == TYPE_LIST_PAGE or type == None:
        data = BeautifulSoup(recv_obj[0], "lxml")
        result_list = data.find_all(name="li", class_="gl-item")
        for k in range(0, len(result_list)):
            i = result_list[k]
            # print([str(i)])
            yield (str(i), TYPE_SINGLE_GOODS, {})
            # r =  parse_list_page(data,worker_obj)
            # print(r)
            # return  r
    if recv_obj[1] == TYPE_SINGLE_GOODS:
        html = BeautifulSoup(data, 'html5lib').find(name="li")

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
            print(data)  # 已经提取到了数据
            push_to_jd(data)
            return False
        except Exception as e:
            print('解析错误' + str(e))
            # traceback.print_exc(e)


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

    str = data["name"]
    with open("/home/jedi/output","w+") as f:
        f.write(str)
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


def after_get(dirver, worker):
    n = 0
    while n < 10:
        print('完成后点击了下一页')
        dirver.find_element_by_class_name('pn-next').click()
        sleep(5)
        worker.push_result(str(dirver.page_source), None)
        print("推入了结果")
        n += 1
