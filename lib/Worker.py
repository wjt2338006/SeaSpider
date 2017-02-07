import threading

from app import jd
from lib.Channel import *
from lib.Downloader import Downloader


class Worker:
    def __init__(self, config, channel):
        self.channel = channel
        self.channel.set_handle(STOP_RUN, self.signal_stop_run)
        self.channel.set_handle(URL_ADD, self.signal_url_add)

        self.config = config
        self.url_queue = queue.Queue()
        self.is_run = False

        self.downloader = []
        self.now_downloader = -1
        for i in self.config["downloader"]:
            d = Downloader(i)
            self.downloader.append(d)

        self.result_queue = queue.Queue()

        self.thread = None
        self.after_get=None

        # 获取传输信道
    def get_channel(self):
        return self.channel

    # 停止运行信号
    def signal_stop_run(self, data):
        self.is_run = False
        return False

    # 添加url信号
    def signal_url_add(self, data):
        if isinstance(data, str):
            self.push_next_url(data)
        return True

    # 获取下载器
    def get_downloader(self):
        if self.now_downloader >= len(self.downloader) - 1:
            self.now_downloader = 0
        else:
            self.now_downloader += 1

        return self.downloader[self.now_downloader]

    def push_next_url(self, url, type=None):
        self.url_queue.put({"url": url, "type": type})

    def push_result(self, data, type):
        self.result_queue.put({"data": data, "type": type})

    # 监控主线程的消息
    def monitor(self):
        while self.is_run:
            r = self.channel.get()
            if r is False:
                break

    # 自己的url处理循环
    def handle_url(self):
        print("url处理循环")
        while self.is_run:
            r = self.url_queue.get()
            print("得到了url",r)
            result_page = self.get_downloader().get(r["url"],self.after_get,self)

            if result_page is not False:
                self.push_result(result_page, r["type"])
            else:
                print("is false")

    # 结果处理循环
    def handle_result(self, parse):
        print("结果处理循环")
        while self.is_run:
            data = self.result_queue.get()
            for (result, data_type) in parse(data["data"], data["type"], self):
                print(["结果",result])
                if result is not None and result is not False:
                    self.push_result(result, data_type)

    # 运行,派出一个线程监控主线程消息,后自己进行url处理
    def run(self):
        def true_run():
            print("worker运行")
            self.is_run = True
            monitor = threading.Thread(target=self.monitor)
            monitor.start()

            #拿到解析函数解析
            module = __import__(self.config["explain"],fromlist=True)
            if "after_get" in self.config:
                self.after_get = getattr(module,self.config["after_get"])

            parse_thread = []
            for i in range(0, self.config["parse_thread"]):
                func = getattr(module, "parse")

                x = threading.Thread(target=lambda: self.handle_result(func))
                x.start()
                parse_thread.append(x)

            self.handle_url()

            monitor.join()
            for i in parse_thread:
                i.join()
            print("线程安全停止")

        self.thread = threading.Thread(target=true_run)
        self.thread.start() #防止阻塞主线程
        print("主线程启动了一个Work子线程")
        return self.thread

    def join(self):
        if self.thread != None:
            self.thread.join()


if __name__ == "__main__":
    config = {
        "id": "9850ac",
        "name": "jd_man",
        "downloader": [
            {
                "type": "selenium",
                "proxy": {
                    "host": "127.0.0.1:1080",
                    "type": "socks5"
                }
            }
        ],
        "explain": "jd",
        "parse_thread": 2
    }
    channel = Channel()
    work = Worker(config, channel)
    work.channel.put(URL_ADD, "http://www.jtcool.com")
    work.run()
