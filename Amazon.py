import json
import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime


class Crawl(scrapy.Spider):
    name="Amazon"
    today = datetime.now().strftime("%Y-%m-%d")
    output = []

    def start_requests(self):
        urls = [
            "https://www.amazon.com.tr/s?k=Cep+Telefonu&i=electronics&rh=n%3A13709907031%2Cp_89%3AApple%7CGENERAL+MOBILE%7COPPO%7COppo+realme%7CSamsung&dc&qid=1630879073&rnid=13493765031&ref=sr_nr_p_89_6", 
        ]
        for url in urls:
            req = scrapy.Request(url, callback=self.parse)
            yield req

    def parseBrand(self, response):
        brand = response.css("#bylineInfo::text").get()
        return brand

    def parse(self, response):
        products = response.css(".s-main-slot.s-result-list .s-result-item.s-asin") 

        for product in products: 
            psku = product.css("div::attr(data-asin)").get().strip()
            pname = product.css(".a-link-normal > span::text").get() 
            purl = "https://www.amazon.com.tr%s" % product.css(".a-link-normal ::attr(href)").get() 
            pimage = product.css("img::attr(src)").get()
            pcategory = response.css(".a-color-state.a-text-bold::text").get().strip()
            pbrand ="3" #yield scrapy.Request(purl, callback=self.parseBrand)
            if (product.css(".a-text-price > span:nth-child(2)::text").get() is not None):
                price = product.css(".a-text-price > span:nth-child(2)::text").get().replace(".", "").replace(",", ".")[:-2]
            else:
                price = 0
            if(product.css(".a-price-whole::text").get() is not None):
                dprice = product.css(".a-price-whole::text").get().replace(".", "")+"."+ product.css(".a-price-fraction::text").get()
            else:
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
            if "a-disabled" not in response.css("ul.a-pagination > li.a-last").attrib["class"]:
                nexturl = "https://www.amazon.com.tr%s" % response.css("ul.a-pagination > li.a-last > a::attr(href)").get()
                yield scrapy.Request(nexturl, callback=self.parse)
        except:
            pass

    def close(self, spider, reason):            
        with open(f"{self.name}_{self.today}.json", "w", encoding="utf-8") as f:
            json.dump(self.output, f, ensure_ascii=False)                

process = CrawlerProcess()
process.crawl(Crawl)
process.start()