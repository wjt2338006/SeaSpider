from selenium import webdriver

from Channel import Channel
from Store import Store


class Worker:
    def __init__(self,use_proxy = None):
        if use_proxy !=None:
            self.driver = webdriver.PhantomJS('/usr/local/bin/phantomjs', service_args=use_proxy)
        else:
            self.driver = webdriver.PhantomJS('/usr/local/bin/phantomjs')

    def run(self,channel,func = None):
        while(True):
            item = channel.read()
            print("get msg:"+str(item))
            if item["type"] == "url":
                self.driver.set_page_load_timeout(15)
                self.driver.get(item["data"])
                Store.store_origin_page(item["data"], self.driver.page_source)

            if item["type"] == "stop":
                break
    def parse(self):
        pass

if __name__ == "__main__":
    service_args = [
        '--proxy=127.0.0.2:1080',
        '--proxy-type=socks5',
    ]
    w = Worker(service_args)
    c = Channel()
    c.write({"type": "url", "data": 'https://search.jd.com/Search?keyword=%E6%9D%AF%E5%AD%90&enc=utf-8&wq=beizi&pvid=iz74vixi.kn7tlh'})
    w.run(c)


