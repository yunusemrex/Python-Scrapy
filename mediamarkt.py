import json
import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime


class Crawl(scrapy.Spider):
    name = "MediaMarkt"
    today = datetime.now().strftime("%Y-%m-%d")
    output = []

    def start_requests(self):
        urls = [
            "https://www.mediamarkt.com.tr/tr/category/_android-telefonlar-675172.html",
        ]
        for url in urls:
            req = scrapy.Request(url, callback=self.parse)
            yield req

    def parse(self, response):
        products = response.css(".products-list li>script")
        for product in products:
            jsonstr = product.css("script::text").get()  
            jsonstr = jsonstr[jsonstr.index("{"):-1] 
            item = json.loads(jsonstr) 
            psku = item["id"]
            pname = item["name"]
            print(pname)
            purl = "https://www.mediamarkt.com.tr/tr/category/_android-telefonlar-675172.html%s" % product.css(
                "h2 > a::attr(href)").get()
            pimage = "https:%s" % product.css(".photo.clickable > img::attr(data-original)").get()
            pcategory = item["dimension10"] 
            pbrand = item["brand"]

            price = item["price"]

            self.output.append({
                "ProductId": psku,
                "ProductSKU": psku,
                "ProductName": pname,
                "ProductURL": purl,
                "ProductImageURL": pimage,
                "ProductCategory": pcategory,
                # "ProductPrice": float(price),
                "Attributes": {
                    "brand": pbrand
                }
            })

        # pagination
        try:
            if response.css("li.pagination-next") is not None:
                nexturl = "https://www.mediamarkt.com.tr%s" % response.css("li.pagination-next > a::attr(href)").get()
                yield scrapy.Request(nexturl, callback=self.parse)
        except:
            pass

    def close(self, spider, reason):
        with open(f"{self.name}_{self.today}.json", "w", encoding="utf-8") as f:
            json.dump(self.output, f, ensure_ascii=False)


process = CrawlerProcess()
process.crawl(Crawl)
process.start()
