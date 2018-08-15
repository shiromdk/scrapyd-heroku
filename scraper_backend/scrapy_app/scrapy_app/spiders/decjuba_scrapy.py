import scrapy
import re
from .mirkcolorselector import sampler_function

class DecjubaSpider(scrapy.Spider):
    name = "decjuba_products"
    start_urls = [
        'https://www.decjuba.com.au/collections/women/dresses',
        'https://www.decjuba.com.au/collections/women/jackets',
        'https://www.decjuba.com.au/collections/women/cardigans',
        'https://www.decjuba.com.au/collections/women/pants',
        'https://www.decjuba.com.au/collections/women/shorts',
        'https://www.decjuba.com.au/collections/women/skirts',
        'https://www.decjuba.com.au/collections/women/tees',
        'https://www.decjuba.com.au/collections/women/tops',
        'https://www.decjuba.com.au/collections/d-luxe/pants',
        'https://www.decjuba.com.au/collections/d-luxe/dl-dresses',
        'https://www.decjuba.com.au/collections/d-luxe/dl-tops'
    ]

    def parse(self, response):

        for product in response.xpath('//p[@class="h6"]'):
            url = "https://www.decjuba.com.au" + product.css('a::attr(href)').extract_first()

            next_page = response.xpath('//span[@class="next"]/a/@href').extract_first()
            if next_page is not None:
                yield response.follow(next_page, self.parse)

            yield scrapy.Request(url, callback=self.parse_product, meta={'start_url':response.request.url})

    def parse_product(self, response):

        class Item(scrapy.Item):
            name = scrapy.Field()
            price = scrapy.Field()
            link = scrapy.Field()
            images = scrapy.Field()
            sizes = scrapy.Field()
            style = scrapy.Field()
            stock = scrapy.Field()
            gender = scrapy.Field()
            colour = scrapy.Field()
            address = scrapy.Field()
            location = scrapy.Field()
            item_type = scrapy.Field()
            vendor_name = scrapy.Field()

        def women_size_converter(size):
            return {
                'XXS': 6,
                'XXS/XS': 8,
                'XS': 8,
                'XS/S': 10,
                'S': 10,
                'S/M': 12,
                'M': 12,
                'M/L': 14,
                'L': 14,
                'L/XL': 16,
                'XL': 16,
                'XL/XXL': 18,
                'XXL': 18,
                'onesize': None,
                '6': 6,
                '8': 8,
                '10': 10,
                '12': 12,
                '14': 14,
                '16': 16,
                '36': 5,
                '37': 6,
                '38': 7,
                '39': 8,
                '40': 9,
                '41': 10,
            }.get(size, size)

        for info in response.xpath('//div[contains(@class, "product-single") and contains(@class, "grid")]'):

            item = Item()
            item['name'] = info.xpath('//div[@itemprop="name"]/text()').extract_first()
            price = re.findall(r'(\d[^\s\\]+)', str(info.xpath('//div[@itemprop="price"]/text()').extract()))
            item['price'] = float(price[0])
            item['link'] = response.url
            sizes = info.xpath('//ul[@class="size-container"]/li/input/@value').extract()
            item['sizes'] = [women_size_converter(i) for i in sizes]
            item['style'] = info.xpath('//div[@id="product-description"]/p/text()').extract()
            item['images'] = ['https:' + i for i in info.xpath('//div[@class="swiper-wrapper"]/div/img').xpath('@src').extract()]
            colour = info.xpath('//span[@class="colour-option"]/img').xpath('@src').extract()
            item['colour'] = [sampler_function(i, 0.3) for i in colour][0]
            item['gender'] = 'Women'
            item['address'] = "Shop 310, Broadway Shopping Centre 1 Bay Street, Broadway, New South Wales 2007, Australia"
            item['location'] = "-33.883835, 151.194704"
            item['stock'] = True
            item['item_type'] = re.findall(r'.+(\/.+)$', response.meta['start_url'])
            item['vendor_name'] = 'Decjuba'
            yield item
