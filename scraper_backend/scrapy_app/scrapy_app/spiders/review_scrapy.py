import scrapy
import re
from .mirkcolorselector import sampler_function

class ReviewSpider(scrapy.Spider):
    name = "review_products"
    start_urls = [
        'https://www.review-australia.com/au/shop/dresses',
        'https://www.review-australia.com/au/shop/tops',
        'https://www.review-australia.com/au/shop/knitwear',
        'https://www.review-australia.com/au/shop/denim',
        'https://www.review-australia.com/au/shop/jackets',
        'https://www.review-australia.com/au/shop/coats',
        'https://www.review-australia.com/au/shop/pants',
        'https://www.review-australia.com/au/shop/skirts',
        'https://www.review-australia.com/au/shop/shorts',
        'https://www.review-australia.com/au/shop/sleepwear'

    ]

    def parse(self, response):

        if response is not None:

            for product in response.xpath('//div[@class="product-image"]'):
                url = "https://www.review-australia.com" + product.css('a::attr(href)').extract_first()
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

        for info in response.xpath('//div[@id="primary"]'):

            item = Item()
            item['link'] = response.url
            item['name'] = info.xpath('//h1[@itemprop="name"]/text()').extract()[0]
            price = info.xpath('//span[@class="price-sales"]/text()').extract()
            item['price'] = float(re.findall(r'(\d*\.\d*)', price[0])[0])
            item['stock'] = True
            item['gender'] = 'Women'
            item['address'] = 'Shop 2051, Westfield Sydney City188 Pitt St Sydney, NSW Australia 2000'
            item['location'] = '-33.869557, 151.208841'
            item['image_urls'] = info.xpath('//img[@class="productthumbnail"]').xpath('@src').extract()
            sizes = info.xpath('//select[@id="va-size"]/option/text()').extract()[1:]
            item['sizes'] = [re.sub(r'(\n)', '', i) for i in sizes]
            item['style'] = info.xpath('//div[@id="replaced-details"]/text()').extract()[0]
            colour_sample_urls = ['https://review-australia.com' + i for i in info.xpath('//a[@class="swatchanchor"]/img').xpath('@src').extract()]
            item['colours'] = [sampler_function(i, 0.3) for i in colour_sample_urls]
            item_type = response.meta['start_url']
            item['item_type'] = re.findall(r'(\w*\w$)', item_type)[0]
            item['vendor_name'] = 'Review'

            #
            # colour = [re.sub(r'.*background-color: ', '', j) for j in info.xpath('//div[@id="filters-product-detail"]/div[@class="color-filter"]/a').xpath('@style').extract()]
            # item['variant'] = {}
            #
            # n = 0
            # for c in colour:
            #     item['variant'][n] = {}
            #     item['variant'][n]['images'] = info.xpath('//div[contains(@class, "visible-md-block") and contains(@class, "visible-lg-block") and contains(@class, "gallery-thumbnails") and contains(@class, "gallery-thumbnails-bottom")]/div[@class="col-md-3"]/div[@class="thumbnail"]/a/img').xpath('@src').extract()
            #     item['variant'][n]['sizes'] = [women_size_converter(i) for i in info.xpath('//select[@class="form-control"]/option').xpath('@value').extract()[2:]]
            #     item['variant'][n]['colour'] = c
            #     n += 1

            yield item
