import scrapy
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, JavascriptException


class ThacoSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["vnexpress.net"]
    start_urls = [
        "https://vnexpress.net/thilogi-cung-cap-giai-phap-van-tai-noi-dia-cho-doanh-nghiep-4588867.html",
        "https://vnexpress.net/oto-kia-ra-mat-o-at-cuoc-tan-cong-tong-luc-cua-xe-han-4367434.html",
        "https://vnexpress.net/cong-ty-cua-ty-phu-tran-ba-duong-thanh-chu-moi-cua-emart-4369369.html"
    ]

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        # options.add_argument("--headless")
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
        self.driver.set_page_load_timeout(10)
        self.wait = WebDriverWait(self.driver, 10)
        print(f'✅ Initialed Chrome driver!')

    def parse(self, response):
        try:
            self.driver.get(response.url)
        except TimeoutException:
            self.driver.execute_script("window.stop();")
        
        self.scroll_page(selector_find = "div.tags h4")  # Dùng để cuộn xuống dư��i để tải thêm nội dung trang web.
        
        title = response.css("h1.title-detail::text").get()
        date = response.css("span.date::text").get()
        desc = response.css("div.sidebar-1 > p.description::text").get()
        content = response.css("article.fck_detail p::text").getall()
        author = response.css("article.fck_detail p > strong::text").get()
        total_comments = response.css("#total_comment::text").get()
        
        
        page_source = self.driver.page_source
        sel = scrapy.Selector(text=page_source)
        tags = sel.css("div.tags h4::text").getall()
        
        yield {
            "title": title,
            "date": date,
            "desc": desc,
            "content": content,
            "author": author,
            "total_comments": total_comments,
            "tags": tags
        }

    # def scroll_page(self, selector_find=None):
    #     max_scrolls = 10
    #     scroll_count = 0

    #     while scroll_count < max_scrolls:
    #         print(f"🔄 Scrolling page {scroll_count + 1}/{max_scrolls}")
    #         try:
    #             # Kiểm tra xem phần tử đã xuất hiện chưa
    #             self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector_find)))
    #             break
    #         except TimeoutException:
    #             # Nếu chưa tìm thấy, cuộn xuống dưới
    #             self.driver.execute_script(f"window.scrollBy({scroll_count*1000}, {(scroll_count+1)*1000});")
    #             scroll_count += 1
    #             time.sleep(1)

    def scroll_page(self, selector_find=None):
        # Giới hạn số lần cuộn để tránh vòng lặp vô hạn
        max_scroll_time = 30  # Tổng thời gian cuộn tối đa (giây)
        scroll_pause_time = 0.5  # Thời gian dừng giữa mỗi lần cuộn (giây)
        total_time = 0

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        while total_time < max_scroll_time:
            try:
                # Kiểm tra xem phần tử đã xuất hiện chưa
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector_find)))
                break
            except TimeoutException:
                pass  # Nếu chưa tìm thấy, tiếp tục cuộn

            try:
                # Thực hiện cuộn xuống dưới một chút
                self.driver.execute_script(f"window.scrollBy({scroll_count*300}, {(scroll_count+1)*300});")
            except JavascriptException as e:
                self.logger.error(f"Lỗi khi cuộn trang: {e}")
                break

            scroll_count += 1

            time.sleep(scroll_pause_time)
            total_time += scroll_pause_time

            # Kiểm tra xem đã cuộn đến cuối trang chưa
            new_height = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
            document_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height >= document_height:
                self.logger.info(f"Đã cuộn đến cuối trang!")
                break

    def closed(self, reason):
        self.driver.quit()
        print(f'❌ Closed Chrome driver!')