#-*- coding:utf-8 -*-
import signal

from lib.Channel import Channel, URL_ADD, STOP_RUN
from lib.Log import Log
from lib.Proxy import Proxy
from lib.Worker import Worker
from lib.Config import Config


def singleton(class_):
    instance = {}

    def get( *args, **kwargs):
        if class_ not in instance:
            instance[class_] = class_(*args, **kwargs)
        return instance[class_]

    return get


import logging

handler = logging.FileHandler('/var/log/sea_spider/logging.log', "a",
                              encoding="UTF-8")
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                # filename='/var/log/sea_spider/logging.log',
                filemode='a',
                 handlers=[handler]
                    )


@singleton
class Master:
    def __init__(self, config_path=None):

        c = Config(config_path)
        self.config = c
        self.worker_num = self.config.get('work_num')
        self.worker_pool = []
        self.config_dict = {
            "kafka_log_host": self.config.get('kafka_log_host'),
            "kafka_log_topic": self.config.get("kafka_log_topic")
        }

        self.log = Log(self.config_dict["kafka_log_host"], self.config_dict["kafka_log_topic"])


    def run(self):
        # 运行几个worker,让他们监听channel
        work_list = self.config.get('work_list')
        if len(work_list) != self.worker_num:
            raise Exception('error worker count')

        for i in range(0, self.worker_num):
            worker = Worker(work_list[i], Channel(),self)
            t = worker.run()
            self.add_work(work_list[i]['id'], worker, t)

        for i in self.worker_pool:
            i["thread"].join()

    def add_work(self, id, work, thread):
        self.worker_pool.append(
            {
                "id": id,
                "obj": work, "thread": thread
            })

    def run_proxy(self):
        self.proxy_list = Proxy(self.config.get("proxy"))
        self.proxy_list.run()


if __name__ == "__main__":
    m = Master("../config/main.json")
    m.run_proxy()
    m.run()
