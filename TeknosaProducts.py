import json
import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime



class Crawl(scrapy.Spider):
    name="Teknosa"
    today = datetime.now().strftime("%Y-%m-%d")
    output = []

    def start_requests(self):
        urls = [
            "https://www.teknosa.com/iphone-ios-telefonlar-c-100001001",  
        ]
        for url in urls:
            req = scrapy.Request(url, callback=self.parse)
            yield req

    def parse(self, response):
        products = response.css("#js-product-list-grid-view .product-item") 

        for product in products:
            psku = product.css("div::attr(data-product-id)").get()
            pname = product.css("div::attr(data-product-name)").get() 
            purl = "https://www.teknosa.com%s" % product.css(".product-image-item a::attr(href)").get() 
            pimage = product.css("img::attr(data-src)").get()
            pcategory = response.css(".box-header div h2 b::text").get()
            pbrand = product.css("div::attr(data-product-brand)").get()

            price = product.css("div::attr(data-product-actual-price)").get()
            dprice = product.css("div::attr(data-product-discounted-price)").get()
            if float(price) == 0:
                ispromotion = 0
                price = dprice
                dprice = 0
            else:
                ispromotion = 1




            self.output.append({
                "ProductId": psku,
                "ProductSKU": psku,
                "ProductName": pname,
                "ProductURL": purl,
                "ProductImageURL": pimage,                      
                "ProductCategory": pcategory,
                "ProductPrice": float(price),
                "ProductDiscountPrice": float(dprice),
                "ProductIsPromoted": bool(ispromotion),
                "Attributes": {
                    "brand": pbrand
                }
            })

        # pagination
        try:
            if "disable" not in response.css(".pagination .pagination-next").attrib["class"]:
                nexturl = "https://www.teknosa.com%s" % response.css(".pagination .pagination-next a::attr(href)").get()
                yield scrapy.Request(nexturl, callback=self.parse)
        except:
            pass

    def close(self, spider, reason):           
        with open(f"{self.name}_{self.today}.json", "w", encoding="utf-8") as f:
            json.dump(self.output, f, ensure_ascii=False)                

process = CrawlerProcess()
process.crawl(Crawl)
process.start()