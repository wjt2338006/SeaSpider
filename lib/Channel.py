import queue


class Channel:
    def __init__(self):
        self.queue = queue.Queue()
        self.func = {}

    def put(self, type, data):
        put_data = {
            "type": type,
            "data": data
        }
        self.queue.put(put_data)

    def get(self):
        get_data = self.queue.get()
        return self.func[str(get_data["type"])](get_data["data"])

    def set_handle(self, type, func):
        self.func[str(type)] = func


STOP_RUN = 0
URL_ADD = 1
