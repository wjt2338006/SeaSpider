from lib.Master import Master

m = Master("./config/main.json")
m.run_proxy()
m.run()