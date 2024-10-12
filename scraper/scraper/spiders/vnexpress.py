from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, JavascriptException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapy
from ..settings import HOST_SELENIUM
from time import sleep
import ssl, os
ssl._create_default_https_context = ssl._create_stdlib_context

class VnexpressSpider(scrapy.Spider):
    name = "vnexpress"
    allowed_domains = ["vnexpress.net"]
    start_urls = [
        "https://vnexpress.net/thilogi-cung-cap-giai-phap-van-tai-noi-dia-cho-doanh-nghiep-4588867.html",
        "https://vnexpress.net/oto-kia-ra-mat-o-at-cuoc-tan-cong-tong-luc-cua-xe-han-4367434.html",
        "https://vnexpress.net/cong-ty-cua-ty-phu-tran-ba-duong-thanh-chu-moi-cua-emart-43609369.html"
    ]

    def __init__(self):
        # self.service = Service(ChromeDriverManager().install())
        # self.driver = webdriver.Chrome(service=self.service, options=self.init_options())
        self.driver = webdriver.Remote(f"http://{HOST_SELENIUM}:4444", options=self.init_options())
        self.driver.set_page_load_timeout(5)
        self.wait = WebDriverWait(self.driver, 3)
        print(f"✅ Initialed Chrome driver!")
    
    def init_options(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--start-maximized")
        # self.chrome_options.add_argument('--headless')
        return self.chrome_options
    
    def parse(self, response):
        # extract data
        url = response.url
        _id = url.split("-")[-1].split(".")[0]
        title = response.css("h1.title-detail::text").get()
        date = response.css("span.date::text").get()
        desc = response.css("div.sidebar-1 > p.description::text").get()
        content = response.css("article.fck_detail p::text").getall()
        author = response.css("article.fck_detail p > strong::text").get()

        # load url
        try:
            self.driver.get(response.url)
        except TimeoutException:
            self.driver.execute_script("window.stop();")
        
        # scrolling
        # page_source = self.driver.page_source
        # sel = scrapy.Selector(text=page_source)
        # if sel.css("#total_comment::text").get() == None:
        self.scroll_page(selector_find="div.ykien_vne.width_common")
        for comment in self.driver.find_elements(By.CSS_SELECTOR,'div.comment_item.width_common'):
            try:
                if self.driver.find_element(By.CSS_SELECTOR, 'p.count-reply > a').is_displayed():
                    self.driver.find_element(By.CSS_SELECTOR, 'p.count-reply > a').click()
                    sleep(1)
            except:
                pass            
        self.scroll_page(selector_find="div.tags h4")
        sleep(1)

        # save screenshot
        self.save_screenshot(f'screenshots/{_id}.png')

        # extract comment
        page_source = self.driver.page_source
        sel = scrapy.Selector(text=page_source)
        tags = sel.xpath('//div[@class="tags"]//h4//text()').getall()
        total_comments = sel.css("#total_comment::text").get()
        comments = []
        for comment in sel.css('#list_comment > div.comment_item.width_common'):
            comment_info = {
                'user_name': comment.css('div.content-comment > p.full_content > span.txt-name > a.nickname::text').get(),
                'user_link': comment.xpath('//div[@class="content-comment"]//p[@class="full_content"]//span[@class="txt-name"]//a[@class="nickname"]').attrib['href'],
                'comment_text': comment.css('div.content-comment > p.full_content::text').get(),
                'comment_date': comment.css('span.time-com::text').get(),
                'count_react': comment.css('div.reactions-total > a.number::text').get(),
                'reaction': {
                    r.css('span > img').attrib['alt']:r.css('strong::text').get() for r in comment.css('div.reactions-total > div.reactions-detail > div.item')
                }
            }

            # check reply to click
            comment_info['sub_comment'] = []
            for sub_comment in comment.css('div.sub_comment_item.comment_item.width_common'):
                sub_comment_info = {
                    'user_name': sub_comment.css('a.nickname::text').get(),
                    'user_link': sub_comment.xpath('//a[@class="nickname"]/@href').get(),
                    'reply_name': sub_comment.css('div.content-comment > p.full_content > span.reply_name > a.reply_name::text').get(),
                    'reply_name_link': sub_comment.xpath('//div[@class="content-comment"]//p[@class="full_content"]//span[@class="reply_name"]//a[@class="reply_name"]').attrib['href'],
                    'comment_text': sub_comment.css('div.content-comment > p.full_content::text').get(),
                    'comment_date': sub_comment.css('span.time-com::text').get(),
                    'count_react': sub_comment.css('div.reactions-total > a.number::text').get(),
                    'reaction': {
                        r.css('span > img').attrib['alt']:r.css('strong::text').get() for r in sub_comment.css('div.reactions-total > div.reactions-detail > div.item') #sub_comment.xpath('//div[@class="reactions-detail"]')
                    }
                }
                comment_info['sub_comment'].append(sub_comment_info)
            comments.append(comment_info)
        print(f'✅ {response.url}')

        yield {
            "_id": _id,
            "url": url,
            "title": title,
            "date": date,
            "desc": desc,
            "content": content,
            "author": author,
            "total_comments": total_comments,
            "tags": tags,
            "comments": comments
        }
    
    def scroll_page(self, selector_find=None, max_scroll_time=30, scroll_pause_time=0.2):
        total_time = 0

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        while total_time < max_scroll_time:
            try:
                # Kiểm tra xem phần tử đã xuất hiện chưa
                if selector_find:
                    self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector_find)))
                print("Đã tìm thấy phần tử!")
                break
            except TimeoutException:
                pass  # Nếu chưa tìm thấy, tiếp tục cuộn

            try:
                # Thực hiện cuộn xuống dưới một chút
                self.driver.execute_script(f"window.scrollBy(0, 300);")
            except JavascriptException as e:
                print(f"Lỗi khi cuộn trang: {e}")
                break

            scroll_count += 1

            # sleep(max_scroll_time)
            total_time += scroll_pause_time

            # Kiểm tra xem đã cuộn đến cuối trang chưa
            new_height = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
            document_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height >= document_height:
                print(f"Đã cuộn đến cuối trang!")
                break

    def closed(self, reason):
        self.driver.quit()
        print(f'❌ Closed Chrome driver!')