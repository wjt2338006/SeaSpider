import json

import requests

from old import Type

url = "http://127.0.0.12/api/input"
class Pull:
    def __init__(self):
        pass
    def pull_page_data(self,type):

        sendData = {"param":
            {
                'api': "pullJdOriginPage",
                'args': {
                   'type':type
                }
            }
        }
        r = requests.post(url, json=sendData)
        result = json.loads(r.text)
        if result["status"] == 200:
            return result["data"]
        else:
            return False

    def pull_single_data(self,type):
        sendData = \
        {
            "param":
            {
                'api': "pullJdOriginSingle",
                'args': {
                    'type': type
                }
            }
        }
        r = requests.post(url, json=sendData)
        result = json.loads(r.text)
        if result["status"] == 200:
            return result["data"]
        else:
            return False


    def pull_url_data(self,type):
        sendData = \
            {
                "param":
                    {
                        'api': "pullUrl",
                        'args': {
                            'type': type
                        }
                    }
            }
        r = requests.post(url, json=sendData)
        result = json.loads(r.text)
        if result["status"] == 200:
            return result["data"]
        else:
            return False


if __name__=="__main__":
    p = Pull()
    # print(p.pull_single_data('jd_goods'))
    # print(p.pull_page_data('jd_list'))
    a = p.pull_url_data(Type.url_jd)
    print(a)
