from lib.Channel import Channel, URL_ADD
from lib.Worker import Worker
from lib.Config import Config


class Master:
    def __init__(self, config_path):

        c = Config(config_path)
        self.config = c
        self.worker_num = self.config.get('work_num')
        self.worker_pool = []

    def run(self):

        # 运行几个worker,让他们监听channel
        work_list = self.config.get('work_list')
        if len(work_list) != self.worker_num:
            raise Exception('error worker count')

        for i in range(0, self.worker_num):
            worker = Worker(work_list[i], Channel())
            t = worker.run()
            self.add_work(work_list[i]['id'], worker, t)
            worker.channel.put(URL_ADD, "https://search.jd.com/Search?keyword=%E6%9D%AF%E5%AD%90&enc=utf-8&wq=%E6%9D%AF%E5%AD%90&pvid=r2455uyi.yhg1ro2a")

        for i in self.worker_pool:
            i["thread"].join()

    def add_work(self, id, work, thread):
        self.worker_pool.append(
            {
                "id": id,
                "obj": work, "thread": thread
            })


if __name__ == "__main__":
    m = Master("../config/main.json")
    m.run()
