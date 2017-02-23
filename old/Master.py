import threading

from Channel import Channel
from Worker import Worker
from spider.jd import parse

from old.Proxy import Proxy


class Master:
    def __init__(self):
        Master.instance = self
        Master.isRun = False
        self.worker_num = 3
        self.worker_pool = []
        self.urlPool = []
        self.proxy = Proxy()
        self.now_worker_index = 0

    def append(self, url, type=None, special=False):
        self.urlPool.append(url)

    #运行
    def run(self):
        if Master.isRun:
            return
        Master.isRun = True

        for i in range(self.worker_num):
            single = {}
            single["worker"] = Worker(self.proxy.get_some_proxy())
            single["id"] = i
            single["channel"] = Channel()
            single["thread"] = threading.Thread(target=single["worker"].run, args=(single["channel"],parse))
            single["thread"].start()

            self.worker_pool.append(single)

        while True:
            nowWork = self.get_worker()  # 现暂时只用第一个

            while len(self.urlPool)>0:
                i = self.urlPool.pop(0)
                nowWork["channel"].write({"type": "url", "data": i})


    #均衡的放出worker
    def get_worker(self):
        worker = self.worker_pool[self.now_worker_index]

        self.now_worker_index+=1
        if self.now_worker_index >=len(self.worker_pool):
            self.now_worker_index = 0

        return worker


    @staticmethod
    def get():
        if Master.instance!=None:
            return Master.instance
        else:
            master  = Master()
            return master

    def append_thread(self):
        while True:
            url = input("input some url")
            if url == None:
                continue
            self.append(url)

Master.instance = None

if __name__ == "__main__":
    a = Master()
    a.append('https://search.jd.com/Search?keyword=%E6%9D%AF%E5%AD%90&enc=utf-8&wq=beizi&pvid=iz74vixi.kn7tlh')
    a = Master.get()

    threading.Thread(target=a.append_thread).start()
    a.run()
