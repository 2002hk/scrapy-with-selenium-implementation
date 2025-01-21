import scrapy
import scrapy, logging, re
from scrapy.utils.log import configure_logging
from scrapy.http.cookies import CookieJar
from scrapy.http import FormRequest
from scrapy.shell import inspect_response
from scrapy.utils.response import open_in_browser
from urllib.parse import urlparse, parse_qs
import argparse
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import time
import undetected_chromedriver as uc
from selenium_stealth import stealth
#from inline_requests import inline_requests
from scraper.items import SearchItem

from scraper.scrapy_selenium2.http import SeleniumRequest, SeleniumRequestUpdatePageSourceAsBody


class BarnetSpider(scrapy.Spider):
    name = "barnet"
    run_headless="NO"
    driver : uc.Chrome = None
    selenium_allow_site=True

    custom_settings = {

#        'FEED_EXPORT_FIELDS': [ "key","title","url" ],

        #driver config
        #"SELENIUM_ENABLE": False,
        "SELENIUM_DRIVER_NAME":"chrome",
        "SELENIUM_DRIVER_ARGUMENTS" : [ ],
        #"SELENIUM_WEBDRIVER_CHROME_OPTIONS": None,
        #"SELENIUM_DRIVER_EXECUTABLE_PATH": None,
        # "SELENIUM_USE_DRIVER_MANUALLY_CREATED":None,
        # "SELENIUM_CALLABLE_DRIVER_CREATED":None,

        #Request Default props
        "SELENIUM_DEFAULT_REQUEST_TIME_SLEEP_MILLI_SEC": None,
        "SELENIUM_DEFAULT_REQUEST_IMPLICITLY_WAIT": None,
        "SELENIUM_DEFAULT_REQUEST_PAGE_SOURCE_AS_BODY": None,
        "SELENIUM_DEFAULT_REQUEST_WAIT_TIME": None,
        "SELENIUM_DEFAULT_REQUEST_WAIT_UNTIL": None,
        "SELENIUM_DEFAULT_REQUEST_SCREENSHOT": None,
        "SELENIUM_DEFAULT_REQUEST_SCRIPT": None,
        "SELENIUM_DEFAULT_REQUEST_SCRIPT_AFTER_TIME_SLEEP_MILLI_SEC": None
    }

    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        if spider.selenium_allow_site:

            spider.settings.set("URLLENGTH_LIMIT", 5000)

            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.140 Safari/537.36"
            options = None

            if spider.run_headless == 'NO':
                spider.log('### Selenium driver - Running Selenium with head')

                options = webdriver.ChromeOptions()
                #options = uc.ChromeOptions()

                # options.add_argument('--headless=new')
                # options.add_argument('--disable-gpu')
                # options.add_argument("--remote-debugging-port=9222")
                # options.headless = True

                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--ignore-ssl-errors')
                options.add_argument('--start-maximized')
                options.add_argument('--disable-notifications')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-popup-blocking')
                options.add_argument("--user-agent={}".format(user_agent))
                #options.add_argument('--blink-settings=imagesEnabled=false')

                options.add_argument('--disable-infobars')

                #load fast
                options.add_argument('--disable-extensions')  # Disable extensions
                options.add_argument('--disable-dev-shm-usage')

            else:
                options = webdriver.ChromeOptions()
                #options = uc.ChromeOptions()

                options.add_argument('--headless=new')
                options.add_argument('--disable-gpu')

                # chrome://inspect/#devices for inspect
                # options.add_argument('--remote-debugging-port=9222')  # Open DevTools port
                # options.add_argument('--remote-allow-origins=*')  # Allow all remote origins
                # options.debugger_address = "127.0.0.1:9222"

                options.headless = True

                options.add_argument('--remote-allow-origins=*')  # Allow all remote origins

                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--ignore-ssl-errors')
                options.add_argument('--start-maximized')
                options.add_argument('--disable-notifications')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-popup-blocking')
                options.add_argument("--user-agent={}".format(user_agent))
                options.add_argument('--disable-infobars')
                #options.add_argument('--blink-settings=imagesEnabled=false')

                #load fast
                #options.add_argument('--disable-extensions')  # Disable extensions
                options.add_argument('--disable-dev-shm-usage')

            #create manually driver
            browser_executable_path = ChromeDriverManager().install()

            #none trackable driver 
            driver = uc.Chrome(options=options, executable_path=browser_executable_path)

            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                )


            #pass options to driver 
            spider.settings.set("SELENIUM_USE_DRIVER_MANUALLY_CREATED", driver )
            spider.settings.set("SELENIUM_WEBDRIVER_CHROME_OPTIONS", options )
            spider.settings.set("SELENIUM_ENABLE", True)
            spider.settings.set("SELENIUM_CALLABLE_DRIVER_CREATED", spider.driver_created)

        return spider
    def driver_created(self):
        # Inject JavaScript using CDP (Chrome DevTools Protocol)
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                """
            }
        )
    def __init__(self, start_date=None, end_date=None, *args, **kwargs):
        super(BarnetSpider, self).__init__(*args, **kwargs)
        self.start_date=start_date
        self.end_date=end_date
    
    def start_requests(self):
        url='https://publicaccess.barnet.gov.uk/online-applications/'

        yield SeleniumRequest(url=url,callback=self.parse,implicitly_wait=120,time_sleep_millisec=1000)

        #return super().start_requests()
    
    def parse(self, response):
        self.log('### Scraping: dosearch ###')
        tabs=self.driver.find_elements(By.XPATH,'//ul[@class="tabs"]/li/a')
        tabs[1].click()

        self.driver.find_element(By.XPATH,'//option[@value="FUL"]').click()
        '''
        #set up argument parser
        parser=argparse.ArgumentParser(description="Take date inputs for Selenium automation.")
        parser.add_argument('--start_date',type=str,required=True)
        parser.add_argument('--end_date',type=str,required=True)

        #parse arguments
        args=parser.parse_args()
        start_date=args.start_date
        end_date=args.end_date'''
        

        start_date_field=self.driver.find_element(By.XPATH,"//input[@type='text' and @name='date(applicationReceivedStart)' and @id='applicationReceivedStart']")
        end_date_field=self.driver.find_element(By.XPATH,"//input[@type='text' and @name='date(applicationReceivedEnd)' and @id='applicationReceivedEnd']")

        start_date_field.send_keys(self.start_date)
        end_date_field.send_keys(self.end_date)

        self.driver.find_element(By.XPATH,'//input[@type="submit" and @value="Search"]').click()
        time.sleep(10)

        yield SeleniumRequestUpdatePageSourceAsBody(url=self.driver.current_url,
                                                    page_source_as_html=self.driver.page_source,
                                                    callback=self.parse_data,
                                                    dont_filter=True #Prevent duplicate filtering if dublicate url so allow
                                                    )

    def parse_data(self,response):
        self.log('## inside parse_data###')
        self.log(response.url)

        while True:
            original_window=self.driver.current_window_handle
            container_link=self.driver.find_elements(By.XPATH,'//ul[@id="searchresults"]//a[1]')
            links=[]
            for link in container_link:
                links.append(link.get_attribute('href'))

            print(links)

            for link in links:
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[1])
                #time.sleep(3)
                self.driver.get(link)
                #time.sleep(3)
                yield SeleniumRequestUpdatePageSourceAsBody(url=self.driver.current_url,
                                                    page_source_as_html=self.driver.page_source,
                                                    callback=self.parse_data_page,
                                                    dont_filter=True #Prevent duplicate filtering if dublicate url so allow
                                                    )
                self.driver.close()
                self.driver.switch_to.window(original_window)
            #driver.switch_to.window(original_window)
            try:
                #self.driver.switch_to.window(original_window)
                time.sleep(2)
                next_page=self.driver.find_element(By.XPATH,'//a[@class="next"]')
                next_page.click()
                time.sleep(2)
            except Exception:
                print('No more pages to scrape')
                break

    def parse_data_page(self,response):
        
        #self.driver.close()
        self.log('##parsing data pages')
        table=response.xpath('//table[@id="simpleDetailsTable"]//tr')

        items=SearchItem()
        
        items['ref']=table[0].css('td ::text').get().strip()
        
        items['alt_red']=table[1].css('td ::text').get().strip()
        items['app_recv']=table[2].css('td ::text').get().strip()
        items['app_val']=table[3].css('td ::text').get().strip()
        items['add']=table[4].css('td ::text').get().strip()
        items['proposal']=table[5].css('td ::text').get().strip()
        items['status']=table[6].css('td ::text').get().strip()
        
        yield items


