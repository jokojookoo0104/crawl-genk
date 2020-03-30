import scrapy
from genk.items import GenkItem
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
import time
from os.path import join,dirname
import re
import pandas as pd
from scrapy.utils.markup import remove_tags
from scrapy import signals
from scrapy.exceptions import DontCloseSpider

class genkcrawlSpider(scrapy.Spider):
    name = 'crawlgenk'
    allowed_domains = ["genk.vn"]
    # folder = dirname(dirname(__file__))
    # filepath = join(folder,"data.csv")
    # data_urls = pd.read_csv(filepath)
    # data_urls_copy = data_urls.copy()
    # data_urls_copy['url'] = 'https://genk.vn'+data_urls_copy['url']
    # start_urls = [url for url in data_urls_copy['url']]
    batch_size = 10000

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler, *args, **kwargs)
        crawler.signals.connect(spider.idle_consume, signals.spider_idle)
        return spider 

    def __init__(self, crawler):
        self.crawler = crawler
        folder = dirname(dirname(__file__))
        filepath = join(folder,"data.csv")
        data_urls = pd.read_csv(filepath)
        data_urls_copy = data_urls.copy()
        data_urls_copy['url'] = 'https://genk.vn'+data_urls_copy['url']
        self.urls = data_urls_copy['url'].values.tolist() # read from file

    def start_requests(self):
        for i in range(self.batch_size):
            url = self.urls.pop(0)
            yield scrapy.Request(url)

    def idle_consume(self):
        """
        Everytime spider is about to close check our urls 
        buffer if we have something left to crawl
        """
        reqs = self.start_requests()
        if not reqs:
            return
        for req in reqs:
            self.crawler.engine.schedule(req, self)
        raise DontCloseSpider
    
    # def start_requests(self):
    #     urls = self.data_urls_copy['url'][:60]
    #     for url in urls:
    #         yield scrapy.Request(url,self.parse)
    #         time.sleep(0.5)
        

    def parse(self, response):
        sohoa_doc = response.xpath("//div[@class='knc-content']")
        if sohoa_doc is not None:
            for docs in response.xpath(".//div[@class='knc-content']/p"):
                yield {
                    'text': remove_tags(docs.get())
                }