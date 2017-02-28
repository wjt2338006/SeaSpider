#-*- coding:utf-8 -*-
import json
import threading
import traceback

import logging

from lib.Channel import *
from lib.Downloader import Downloader
from lib.Log import Log
from lib.MsgQueue import MsgQueue
from lib.exception.Exception import ParseError


class Worker:
    def __init__(self, config, channel, master):
        self.channel = channel
        self.channel.set_handle(STOP_RUN, self.signal_stop_run)
        # self.channel.set_handle(URL_ADD, self.signal_url_add)

        self.config = config

        # url接受频道
        tmp_url_queue = config["url_queue"]
        self.url_queue = MsgQueue(tmp_url_queue["host"], tmp_url_queue["topic"], tmp_url_queue["consumer_group"])

        # 结果批处理频道
        tmp_result_queue = config["result_queue"]
        self.result_queue = MsgQueue(tmp_result_queue["host"], tmp_result_queue["topic"],
                                     tmp_result_queue["consumer_group"])

        # 初始化错误处理频道
        tmp_error_queue = config["error_queue"]
        self.error_queue = MsgQueue(tmp_error_queue["host"], tmp_error_queue["topic"],
                                    tmp_error_queue["consumer_group"])

        tmp_final_queue = config["final_queue"]
        self.final_queue = MsgQueue(tmp_final_queue["host"], tmp_final_queue["topic"])

        # 下载器初始化
        self.downloader = []
        self.now_downloader = -1
        for i in self.config["downloader"]:
            d = Downloader(i)
            self.downloader.append(d)

        # 其他变量初始化
        self.is_run = False
        self.thread = None
        self.after_get = None
        self.id = self.config["id"]
        self.master = master

    def get_channel(self):
        return self.channel

    # 停止运行信号
    def signal_stop_run(self, data):
        self.is_run = False
        return False

    #
    # # 添加url信号
    # def signal_url_add(self, data):
    #     if isinstance(data, str):
    #         self.push_next_url(data)
    #     return True

    # 获取下载器，目前只是按照顺序来获取
    def get_downloader(self):
        if self.now_downloader >= len(self.downloader) - 1:
            self.now_downloader = 0
        else:
            self.now_downloader += 1

        return self.downloader[self.now_downloader]

    def log(self, level, type, index, msg, context={}):
        m = self.master
        m.log.log(self.id, level, type, index, msg, context)
        print("输出log")

    # 监控主线程的消息
    def monitor(self):
        while self.is_run:
            r = self.channel.get()
            if r is False:
                break

    # url处理循环
    def handle_url(self, handle_func):
        print("url处理循环")
        for get_url_data in self.url_queue.consume():
            print("url:", get_url_data)
            try:
                if not self.is_run:
                    break
                data = get_url_data.value.decode()

                recv_obj = json.loads(data)
                # 调用客户函数，其应该返回一个迭代器
                d = self.get_downloader()
                for result in handle_func(d, recv_obj, self.log):  # other留着以后使用
                    if result is not False:
                        send_str = json.dumps(result)  # 这个结果的结构完全交给用户脚本
                        self.result_queue.produce(send_str.encode("utf-8"))
                    else:
                        print("is false ,means EOF")
            except Exception as e:
                # print("url_handle_error",traceback.format_exc())
                self.log(Log.Error, "url_handle_error", None, traceback.format_exc(), get_url_data.value.decode())
            finally:
                self.url_queue.commit_offset()

    # 结果处理循环
    def handle_result(self, parse):
        for data in self.result_queue.consume():
            if not self.is_run:
                break
            try:
                recv_obj = json.loads(data.value.decode("utf-8"))

                for result in parse(recv_obj, self.log, self.final_queue):
                    if result is not False:
                        send_str = json.dumps(result)  # 这个结果的结构完全交给用户脚本
                        self.result_queue.produce(send_str.encode("utf-8"))
            except ParseError as pe:
                # print("result error", traceback.format_exc())
                error_data = {"data": recv_obj, "error": traceback.format_exc()}
                self.error_queue.produce(json.dumps(error_data).encode())
            except Exception as e:
                print("result error", traceback.format_exc())
                self.log(Log.Error, "result_handle_error", None, traceback.format_exc(), data.value.decode())
            finally:
                self.result_queue.commit_offset()

    # 运行,派出一个线程监控主线程消息,后自己进行url处理
    def run(self):
        def true_run():
            print("worker运行")
            self.is_run = True

            # 启动一个和主线程沟通的线程
            monitor = threading.Thread(target=self.monitor)
            monitor.start()

            # 拿到解析函数解析
            module = __import__(self.config["explain"], fromlist=True)

            # 启动解析线程
            parse_thread = []
            for i in range(0, self.config["parse_thread"]):
                parse_func = getattr(module, "parse")

                x = threading.Thread(target=lambda: self.handle_result(parse_func))
                x.start()
                parse_thread.append(x)

            # 阻塞处理url
            handle_func = getattr(module, "handle")
            self.handle_url(handle_func)

            # 等待结束
            monitor.join()
            for i in parse_thread:
                i.join()
            print("线程安全停止")

        self.thread = threading.Thread(target=true_run)
        self.thread.start()  # 防止阻塞主线程
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
