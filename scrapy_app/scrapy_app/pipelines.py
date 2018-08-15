import json
from scrapy_manager.models import ScrapyItem, Product, ProductVendor,ProductImage, Attribute, ProductAttribute


class ScrapyAppPipeline(object):
    def __init__(self, unique_id, *args, **kwargs):
        self.unique_id = unique_id
        self.items = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            unique_id=crawler.settings.get('unique_id'), # this will be passed from django view
        )

    def close_spider(self, spider):
        # And here we are saving our crawled data with django models.
        item = ScrapyItem()
        item.unique_id = self.unique_id
        item.name = json.dumps(self.items)
        item.save()

    def process_item(self, item, spider):
        """
        Process each item that comes through from the spider
        """
        def vendor_id(spider_name):
            """
            Pseudo switch case statement to get vendor id from spider name
            """
            return{
                'review_products':1,
                'sol_alpaca_products':2,
                'not_sol':3,
                'decjuba_products':4,
                'loverthelabel_products':5
                }.get(spider_name)

        def attribute_to_key(attr):
            return{
                'style':1,
                'gender':2,
                'item_type':3,
                'size':4,
                'colour':5
            }.get(attr)

        v_id = vendor_id(spider.name)
        # Create/Update vendor
        vendor, vendor_created = ProductVendor.objects.get_or_create(id=v_id)
        vendor.name = item['vendor_name']
        vendor.address = item['address']
        vendor.geolocation = item['location']
        vendor.save()

        id = item['link']
        # Create update product
        product, created = Product.objects.get_or_create(url=id)
        product.name = item['name']
        product.stock = item['stock']
        product.vendor_id = vendor
        product.save()

        # Adding all the attributes to a product
        gen_atr, gac = Attribute.objects.get_or_create(id=2, name="Gender")
        gender, gender_created = ProductAttribute.objects.get_or_create(product=product, attribute=gen_atr, attribute_value=item['gender'])
        it_atr, itc = Attribute.objects.get_or_create(id=3, name="Item Type")
        item_type, item_t_created = ProductAttribute.objects.get_or_create(product=product, attribute=it_atr, attribute_value=item['item_type'])
        style_atr, stc = Attribute.objects.get_or_create(id=1, name="Style")
        style_type, style_created = ProductAttribute.objects.get_or_create(product=product, attribute=style_atr, attribute_value=item['style'])


        # Adding all sizes to attribute
        sizes = item['sizes']
        size_atr, size_tc = Attribute.objects.get_or_create(id=4, name="Size")
        for size in sizes:
            size_type, size_created = ProductAttribute.objects.get_or_create(product=product, attribute=size_atr, attribute_value=size)

        colours = item['colours']
        colour_atr, ctc = Attribute.objects.get_or_create(id=5,name="Colour")
        for colour in colours:
            colour_type, colour_created = ProductAttribute.objects.get_or_create(product=product, attribute=colour_atr, attribute_value=colour)

        # Adding all images

        images = item['image_urls']
        for image in images:
            image_entry, imc = ProductImage.objects.get_or_create(product=product,image_url=image)
        return item
