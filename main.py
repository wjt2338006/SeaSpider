#-*- coding:utf-8 -*-
from importlib import reload

from lib.Master import Master
import sys
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

m = Master("./config/main.json")
m.run_proxy()
m.run()