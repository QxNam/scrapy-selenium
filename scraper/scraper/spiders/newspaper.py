import scrapy
# from scrapy_selenium import SeleniumRequest
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ThacoSpider(scrapy.Spider):
    name = "newspaper"
    allowed_domains = ["vnexpress.net"]
    start_urls = [
        "https://vnexpress.net/thilogi-cung-cap-giai-phap-van-tai-noi-dia-cho-doanh-nghiep-4588867.html",
        "https://vnexpress.net/oto-kia-ra-mat-o-at-cuoc-tan-cong-tong-luc-cua-xe-han-4367434.html",
        "https://vnexpress.net/cong-ty-cua-ty-phu-tran-ba-duong-thanh-chu-moi-cua-emart-4369369.html"
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse)

    # def parse(self, response):
    #     # //span[@class="date"]
    #     title = response.css("h1.title-detail::text").get()
    #     date = response.css("span.date::text").get()
    #     desc = response.css("div.sidebar-1 > p.description::text").get()
    #     # content = response.css("article.fck_detail p::text").getall()
    #     total_comments = response.css("#total_comment::text").get()
        
    #     yield {
    #         "title": title,
    #         "date": date,
    #         "desc": desc,
    #         # "content": content,
    #         "total_comments": total_comments
    #     }

    def parse(self, response):
        driver = response.request.meta["driver"]
        # # scroll to the end of the page 10 times
        # for _ in range(0, 10):
        #     # scroll down by 10000 pixels
        #     ActionChains(driver) \
        #         .scroll_by_amount(0, 10000) \
        #         .perform()

        # wait = WebDriverWait(driver, timeout=60)
        # wait.until(lambda driver: driver.find_element(By.ID, "total_comment").is_displayed())
        
        title = response.css("h1.title-detail::text").get()
        date = response.css("span.date::text").get()
        desc = response.css("div.sidebar-1 > p.description::text").get()
        content = response.css("article.fck_detail p::text").getall()
        author = response.css("article.fck_detail p > strong::text").get()
        total_comments = response.css("#total_comment::text").get()
        tags = response.css("div.tags h4::text").getall()


        yield {
            "title": title,
            "date": date,
            "desc": desc,
            "content": content,
            "author": author,
            "total_comments": total_comments,
            "tags": tags
        }