import scrapy
import re
from .mirkcolorselector import sampler_function

class LoversSpider(scrapy.Spider):
    name = "loverthelabel_products"
    start_urls = [
        'https://www.loverthelabel.com/collections/dresses?page=1',
        'https://www.loverthelabel.com/collections/dresses?page=2',
        'https://www.loverthelabel.com/collections/dresses?page=3',
        'https://www.loverthelabel.com/collections/dresses?page=4',
        'https://www.loverthelabel.com/collections/tops?page=1',
        'https://www.loverthelabel.com/collections/tops?page=2',
        'https://www.loverthelabel.com/collections/skirt?page=1',
    ]

    def parse(self, response):

        if response is not None:

            for product in response.xpath('//a[@class="grid-view-item__link"]'):
                url = "https://www.loverthelabel.com" + product.css('a::attr(href)').extract_first()
                yield scrapy.Request(url, callback=self.parse_product, meta={'start_url':response.request.url})

    def parse_product(self, response):

        class Item(scrapy.Item):
            name = scrapy.Field()
            link = scrapy.Field()
            price = scrapy.Field()
            image_urls = scrapy.Field()
            sizes = scrapy.Field()
            style = scrapy.Field()
            stock = scrapy.Field()
            colours = scrapy.Field()
            gender = scrapy.Field()
            address = scrapy.Field()
            location = scrapy.Field()
            item_type = scrapy.Field()
            vendor_name = scrapy.Field()

        for info in response.xpath('//div[contains(@class, "product-template__container") and contains(@class, "page-width")]'):
            item = Item()
            item['link'] = response.url
            item['name'] = info.xpath('//h1[@itemprop="name"]/text()').extract_first()
            item['price'] = info.xpath('//span[@itemprop="price"]').xpath('@content').extract_first()
            item['image_urls'] = ['https:' + i for i in info.xpath('//img[@class="image-featured"]').xpath('@src').extract()]
            sizes = [re.sub(r'(\s-.*)', '', i) for i in info.xpath('//select[@id="SingleOptionSelector-0"]/option/text()').extract()]
            sizes_two = [re.sub(r'(\n.*)', '', i) for i in sizes]
            item['sizes'] = [re.sub(r'(AU\s)', '', i) for i in sizes_two][1:]
            item['style'] = info.xpath('//div[@itemprop="description"]/p/text()').extract()
            item['colours'] = sampler_function(item['image_urls'][0], 0.3)
            item['stock'] = True
            item['gender'] = 'Women'
            item['address'] = "The Strand Arcade Shop 69-71, Level 1/412-414 George St, Sydney NSW 2000"
            item['location'] = "-33.869459, 151.207524"
            item['item_type'] = re.findall(r'\w+?(?=\?)', response.meta['start_url'])
            item['vendor_name'] = 'Lover'
            yield item
