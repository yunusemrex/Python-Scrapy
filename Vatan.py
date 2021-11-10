import json
import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime



class Crawl(scrapy.Spider):
    name="Vatan"
    today = datetime.now().strftime("%Y-%m-%d")
    output = []

    def start_requests(self):
        urls = [
            "https://www.vatanbilgisayar.com/cep-telefonu-modelleri/",  
        ]
        for url in urls:
            req = scrapy.Request(url, callback=self.parse)
            yield req

    def parse(self, response):
        products = response.css(".wrapper-product--list-page .product-list--list-page") 

        for product in products: 
            psku = product.css(".product-list__product-code::text").get().strip()
            pname = product.css(".product-list__product-name::text").get().strip() 
            purl = "https://www.vatanbilgisayar.com/cep-telefonu-modelleri%s" % product.css(".product-list__link ::attr(href)").get() 
            pimage = product.css("img::attr(data-src)").get()
            pcategory = response.css(".wrapper-detailpage-header__title::text").get().strip()
            pbrand = product.css(".product-list__product-name::text").get().strip().split()[0]

            price = product.css(".product-list__price::text").get().replace(".", "") + product.css(".product-list__decimals::text").get().replace(",", ".")
            dprice = 0
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

        
        try:
            if response.css("ul.pagination span[class='icon-angle-right']").get() is not None:
                nexturl = "https://www.vatanbilgisayar.com%s" % response.xpath("//ul[@class='pagination']/li[position() = last()]/a/@href").get()
                yield scrapy.Request(nexturl, callback=self.parse)
        except:
            pass

    def close(self, spider, reason):            
        with open(f"{self.name}_{self.today}.json", "w", encoding="utf-8") as f:
            json.dump(self.output, f, ensure_ascii=False)                

process = CrawlerProcess()
process.crawl(Crawl)
process.start()