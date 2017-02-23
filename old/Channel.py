class Channel:
    def __init__(self):
        self.lock = False
        self.msgList = []
        pass

    def read(self):
        while len(self.msgList) == 0:
            continue

        self.lock = True
        item = self.msgList.pop(0)
        self.lock = False

        return item

    def write(self,item):
        self.lock = True
        self.msgList.append(item)
        self.lock = False

    '''
    消息格式
    type => url/stop
    data =>
    '''

