from selenium import webdriver


class Downloader:
    def __init__(self, config, bin_path='/usr/local/bin/phantomjs'):
        self.type = config['type'] # 选择下载器类型
        if self.type == 'selenium':
            s_args = []
            if 'proxy' in config:
                s_args.append("--proxy=%s"%config["proxy"]["host"])
                s_args.append("--proxy-type=%s" % config["proxy"]["type"])

            self.dirver = webdriver.PhantomJS(bin_path, service_args=s_args)
    def get(self,url):
        try:
            data = self.dirver.get(url)
            if len(self.dirver.page_source) == 0:
                raise Exception('error empty page')
            return str(data)

        except Exception as e:
            print(e)#todo log
            return False