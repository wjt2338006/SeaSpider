#-*- coding:utf-8 -*-
from importlib import reload

from lib.Master import Master
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

m = Master("./config/main.json")
m.run_proxy()
m.run()