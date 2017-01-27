import json

import requests

from Type import url_jd

url = "http://127.0.0.12/api/input"


class Store:
    @staticmethod
    def store_origin_single(data, k):
        sendData = \
            {"param":
                {
                    'api': "pushJdOriginSingle",
                    'args': {
                        'other': {'index': k},
                        'data': data
                    }
                }
            }
        r = requests.post(url, json=sendData, timeout=30)
        result = json.loads(r.text)
        if result["status"] == 200:
            print('ok,push single page')
            pass
        else:
            print('server error')

    @staticmethod
    def store_origin_page(page_url, data):
        url = "http://127.0.0.12/api/input"
        sendData = \
            {"param":
                {
                    'api': "pushJdOriginPage",
                    'args': {
                        'page_url': page_url,
                        'page_data': data
                    }
                }
            }
        r = requests.post(url, json=sendData, timeout=30)
        result = json.loads(r.text)
        if result["status"] == 200:
            print('ok,i get some page')
            pass
        else:
            print('server error')

    @staticmethod
    def storeJd(data):
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
            'data_order': data["order"]
        }

        r = requests.post(url, json=sendData)
        result = json.loads(r.text)

        if result["status"] == 200:
            print('ok,i get some page')
            pass
        else:
            print('server error')

    @staticmethod
    def sendErrorExplainLog(data, error_msg):
        data = str(data)
        url = "http://127.0.0.12/api/input"
        sendData = {"param":
            {
                'api': "pushJdErrorExplain",
                'args': {
                    'data': data,
                    'error_msg': str(error_msg)
                }
            }
        }
        print(sendData)
        r = requests.post(url, json=sendData)
        result = json.loads(r.text)
        if result["status"] == 200:
            print('error log send')
            pass
        else:
            print('server error')  # todo 日志化

    @staticmethod
    def send_url(type, store_url):
        url = "http://127.0.0.12/api/input"
        sendData = \
            {"param":
                {
                    'api': "pushUrl",
                    'args': {
                        'type': type,
                        'url': store_url
                    }
                }
            }
        r = requests.post(url, json=sendData)
        result = json.loads(r.text)
        if result['status'] == 200:
            print('log send')
        else:
            print('send log error')


if __name__ == "__main__":
    # Store.store_origin_single("xxx", 1)
    Store.send_url(url_jd, url)