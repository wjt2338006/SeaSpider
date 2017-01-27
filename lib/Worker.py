import threading

from lib.Channel import *


class Worker:
    def __init__(self, config, channel):
        self.channel = channel
        self.channel.set_handle(STOP_RUN, self.stop_run)
        self.channel.set_handle(URL_ADD, self.url_add)

        self.config = config
        self.url_queue = []
        self.is_run = False

    def get_channel(self):
        return self.channel

    def stop_run(self, data):
        self.is_run = False
        return False

    def url_add(self, data):
        if isinstance(data, (str)):
            self.url_queue.put(data)
        return True

    # 监控主线程的消息
    def monitor(self):
        while self.is_run:
            r = self.channel.get()
            if r is False:
                break

    # 自己的url处理循环
    def handle_url(self):
        while self.is_run:
            r = self.url_queue.get()
            #确定我自己的解析器,动态调用

    # 运行,派出一个线程监控主线程消息,剩下的自己进行url处理
    def run(self):
        self.is_run = True
        monitor = threading.Thread(target=self.monitor)
        monitor.run()

        #todo 把downloader实例化出来
        self.handle_url()

    