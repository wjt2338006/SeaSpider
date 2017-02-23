import json
import traceback

from Pull import Pull
from bs4 import BeautifulSoup

from old.Store import Store


# 将列表页分割分成小块


def block_divde(src_data):
    print(src_data)
    data = BeautifulSoup(src_data, "lxml")
    result_list = data.find_all(name="li", class_="gl-item")
    print(result_list)
    for k in range(len(result_list)):
        i = result_list[k]
        Store.store_origin_single(str(i), str(k))


# 对每个小块进行解析
def block_explain(src_data, index):
    i = BeautifulSoup(src_data, 'html5lib').find(name="li")
    print(i)
    data = {}
    data["jd_id"] = ""
    data["name"] = ""
    try:
        name_div = i.find(name="div", class_="p-name")
        data["name"] = name_div.a.em.get_text()
        data["price"] = i.find(name="div", class_="p-price").strong.i.get_text()
        data["detail_url"] = name_div.a["href"]

        try:
            data["jd_id"] = i["data-spu"]
        except Exception as e:
            print('fail get sku')
            data["jd_id"] =" "

        data["seller_name"] = explain_shop(i, data)
        data["order"] = index

        Store.storeJd(data)
        return data
    except Exception as e:
        print("解析发生错误" + str(e))
        traceback.print_exc(e) #报错信息写入
        return False
        # Store.sendErrorExplainLog(i,str(e)+" " +str(data["jd_id"])+" "+str(data["name"]))


def explain_shop(div,data):
    seller_name = ""
    try:
        seller_name = div.find(name="div", class_="p-shop").span.a["title"]
        return seller_name
    except Exception as e:
        print("seller_name 无法找到")
        seller_name = ""
        Store.sendErrorExplainLog(div, str(e) + " " + str(data["jd_id"]) + " " + str(data["name"]))
        return str(seller_name)

#
# def run_worker():
#     service_args = [
#         '--proxy=127.0.0.2:1080',
#         '--proxy-type=socks5',
#     ]
#     w = Worker(service_args)
#     c = Channel()
#     c.write({"type": "url",
#              "data": 'https://search.jd.com/Search?keyword=%E6%9D%AF%E5%AD%90&enc=utf-8&wq=beizi&pvid=iz74vixi.kn7tlh'})
#     w.run(c)
#  todo url做了,现在下一步是准备找到下一页的url进行遍历了
if __name__ == "__main__":
    # socks.set_default_proxy(socks.SOCKS5, "127.0.0.2", 1080)
    # socket.socket = socks.socksocket
    # socket._real_socket = socket.socket
    # proxy = Proxy({'socksProxy':'127.0.0.1:1080'})


    # url = 'https://search.jd.com/Search?keyword=%E6%9D%AF%E5%AD%90&enc=utf-8&wq=beizi&pvid=iz74vixi.kn7tlh'
    # #url = "http://www.google.com"
    # # r = requests.get(url, proxies={"http": 'socks5://127.0.0.2:1080',
    # #                                'https': 'socks5://127.0.0.2:1080'})
    # # r = requests.get(url)
    # # print(r.text)
    #
    # service_args = [
    #     '--proxy=127.0.0.4:1080',
    #     '--proxy-type=socks5',
    # ]
    # driver = webdriver.PhantomJS('/usr/local/bin/phantomjs',service_args=service_args)
    # driver.set_page_load_timeout(20)
    # driver.get(url)
    # print(driver.page_source)

    p = Pull()
    # data = p.pull_page_data('jd_list')
    # if False != data and len(data) != 0:
    #     block_divde(str(data["page_data"]))
    # else:
    #     print('no data')


    data = p.pull_single_data('jd_goods')
    data = block_explain(data["single_data"], json.loads(data["single_other"])["index"])
    print(data)
