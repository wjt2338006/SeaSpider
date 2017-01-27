from lib import Channel
from lib import Config
from lib import Worker


class Master:
    def __init__(self, config_path):
        self.worker_num = self.config.get('work_num')
        self.worker_pool = []
        self.config = Config(config_path)

    def run(self):

        # 运行几个worker,让他们监听channel
        work_list = self.config.get('worker_list')
        if len(work_list) != self.worker_num:
            raise Exception('error worker count')

        for i in range(0, self.worker_num):
            worker = Worker(work_list[i], Channel())
            self.add_work(work_list[i]['id'], worker)


    def add_work(self,id,work):
        self.worker_pool.append({
            "id": id,
            "obj": work})
