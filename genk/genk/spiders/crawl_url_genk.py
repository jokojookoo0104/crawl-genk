import scrapy
from genk.items import StackItem
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options



class SohoaSpider(scrapy.Spider):
    name = 'genk'
    allowed_domains = ["genk.vn"]
    start_urls = [
        'https://genk.vn/dien-thoai.chn',
        'https://genk.vn/digital-marketing.chn',
        'https://genk.vn/may-tinh-bang.chn',
        'https://genk.vn/media.chn',
        'https://genk.vn/lich-su.chn',
        'https://genk.vn/tri-thuc.chn',
        'https://genk.vn/tan-man.chn',
        'https://genk.vn/y-tuong-sang-tao.chn',
        'https://genk.vn/thu-thuat.chn',
        'https://genk.vn/tin-ict.chn',
        'https://genk.vn/song.chn',
        'https://genk.vn/apps-games.chn',
        'https://genk.vn/do-choi-so.chn',
        ]
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome('./chromedriver',options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def scroll_until_loaded(self):
        count = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(7)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                element1= self.driver.find_element_by_xpath('//div[@class="wrapperbtn"]/a')
                self.driver.execute_script("arguments[0].click();",element1)
                time.sleep(7)
                print('count:',count)
                count +=1
                if count == 5:
                    break
            
            last_height = new_height
            print('height-page',last_height)

        scrapy_selector = Selector(text = self.driver.page_source)
        return scrapy_selector


    def parse(self, response):
        # sohoa_doc = response.xpath("//div[@class='knc-content']")
        # if sohoa_doc is not None:
        #     for docs in response.xpath(".//div[@class='knc-content']/p"):
        #         yield {
        #             'text': docs.get()
        #         }
        self.driver.get(response.url)
        
        scrapy_selector=self.scroll_until_loaded()
        posts = scrapy_selector.xpath('//div[@class="knswli-right elp-list"]/h4')
        print('cccccccccc',posts)
        for post in posts:
            item = StackItem()
            item['title'] = post.xpath(
                'a[@class="show-popup visit-popup"]/text()').extract_first()
            item['url'] = post.xpath(
                'a[@class="show-popup visit-popup"]/@href').extract_first()
            yield item