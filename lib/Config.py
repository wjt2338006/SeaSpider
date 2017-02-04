import json
import os


class Config:
    def __init__(self, path):
        self.path = path
        self.reload()

    def get(self, key):
        key_list = key.split('.')
        r = self.config

        for i in key_list:
            if isinstance(r, list):
                r = r[int(i)]
            else:
                r = r[str(i)]
        return r

    def reload(self):
        config_file = open(self.path, 'r')
        self.config = json.loads(config_file.read())


if __name__ == "__main__":
    c = Config('../config/main.json')
    r = c.get('work_list.0.id')
    print(r)
