from selenium import webdriver


class Downloader:
    def __init__(self,config):
        self.type = config['type'] # 选择下载器类型
        if self.type == 'selenium':
            s_args = []
            if 'proxy' in config:
                s_args.append("--proxy=%"%config["proxy"]["host"])
                s_args.append("--proxy-type=%" % config["proxy"]["type"])
            self.dirver = webdriver.PhantomJS('/usr/local/bin/phantomjs', service_args=s_args)
    def get(self,url):
        try:
            data = self.dirver.get(url)
            if len(self.dirver.page_source) == 0:
                raise Exception('error empty page')

            #todo consume this url
            return data
        except Exception as e:
            print(e)#todo log
            pass