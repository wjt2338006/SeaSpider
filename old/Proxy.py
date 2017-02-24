import subprocess

import sys


class Proxy:
    def __init__(self, proxy_config=None):
        self.config = proxy_config
        self.now_locate = 0

    def get_some_proxy(self):
        if len(self.config) == 0:
            return None
        now = self.config[self.now_locate]
        self.now_locate += 1
        if not self.now_locate < len(self.config):
            self.now_locate = 0

        return now["proxy"]

    def run(self):
        for proxy in self.config:
           subprocess.Popen("sslocal -c "+proxy["config"], stdout=sys.stdout, shell=True)




if __name__ == "__main__":
    p = Proxy()
    p.run()
