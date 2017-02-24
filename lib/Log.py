import json

import time

from lib.MsgQueue import MsgQueue


class Log:
    Error = "error"
    Debug = "debug"
    Info = "info"
    Warn = "warn"
    Danger = "danger"

    def __init__(self, host, topics):
        self.topics = topics
        self.host = host

        self.produce = MsgQueue(host, topics)

    def log(self, worker, level, type , index, msg, context={}):
        log_str = '[%s] [%s] [%s] [%s] [%s] %s %s' % ( time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) ,worker, level, type, index, msg, json.dump(context))
        self.produce.produce(log_str)


