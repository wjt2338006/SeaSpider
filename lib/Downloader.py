from selenium import webdriver
from selenium.webdriver import DesiredCapabilities


class Downloader:
    def __init__(self, config, bin_path='/usr/local/bin/phantomjs'):
        self.type = config['type']  # 选择下载器类型
        if self.type == 'selenium':
            s_args = []
            if 'proxy' in config:
                s_args.append("--proxy=%s" % config["proxy"]["host"])
                s_args.append("--proxy-type=%s" % config["proxy"]["type"])

            caps = DesiredCapabilities.PHANTOMJS
            caps["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, " \
                                                        "like Gecko) Ubuntu Chromium/55.0.2883.87 Chrome/55.0.2883.87" \
                                                        " Safari/537.36 "

            self.driver = webdriver.PhantomJS(bin_path, service_args=s_args, desired_capabilities=caps)

    def get(self, url, after_get_page=None,worker=None):
        try:
            self.driver.get(url)
            data = self.driver.page_source
            if after_get_page is not None:
                after_get_page(self.driver,worker)
            if len(data) == 0:
                raise Exception('error empty page')
            return str(data)

        except Exception as e:
            print(e)  # todo log
            return False
