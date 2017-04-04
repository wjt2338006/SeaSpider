import time

from lib.model_extend.ModelExtend import ModelExtend

#未完成调度器
class Monitor:
    @classmethod
    def listenTask(cls):
        data = ModelExtend.get({"$order":"watch_deadline","$and":[["watch_deadline","<",time.time()/1000 + 600]]},"spider.shop_watch.watch_id")
        if not data :
            return []
        keyword_dict = {}
        for i in  data:
            if i["watch_index"] in keyword_dict:
                keyword_dict[i["watch_index"]].append(i)
            else:
                keyword_dict[i["watch_index"]] = [i]
