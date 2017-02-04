from lib import Channel
from lib import Worker
from lib.Config import Config

class Master:
    def __init__(self, config_path):

        c = Config(config_path)
        self.config = c
        self.worker_num = self.config.get('work_num')
        self.worker_pool = []


    def run(self):

        # 运行几个worker,让他们监听channel
        work_list = self.config.get('worker_list')
        if len(work_list) != self.worker_num:
            raise Exception('error worker count')

        for i in range(0, self.worker_num):
            worker = Worker(work_list[i], Channel())
            self.add_work(work_list[i]['id'], worker)
            worker.run()


    def add_work(self, id, work):
        self.worker_pool.append({
            "id": id,
            "obj": work})


if __name__ == "__main__":
    m = Master("../config/main.json")
    m.run()
