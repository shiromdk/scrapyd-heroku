"""
Views - Contains all the view functions
"""
import scrapy
from uuid import uuid4
from urllib.parse import urlparse
from django.core import serializers
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from scrapyd_api import ScrapydAPI
from scrapy_manager.models import ScrapyItem
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from itertools import chain
import scrapy_app
# Importing the spiders
from scrapy_app.scrapy_app.spiders.lover_the_label_scrapy import LoversSpider
from scrapy_app.scrapy_app.spiders.decjuba_scrapy import DecjubaSpider
from .models import Product, ProductAttribute, ProductImage
from django.db.models import Q
# connect scrapyd service
SCRAPYD = ScrapydAPI('https://scrapydmirk.herokuapp.com/')


def is_valid_url(url):
    """
    is_valid_url - Checks if url given is a valid url
    """
    validate = URLValidator()
    try:
        validate(url) # check if url format is valid
    except ValidationError:
        return False

    return True


@csrf_exempt
@require_http_methods(['POST', 'GET']) # only get and post
def query(request):
    style = request.POST.get('style',None)
    itemtype = request.POST.get('itemtype',None)
    gender = request.POST.get('gender',None)
    colour = request.POST.get('colour',None)
    size = request.POST.get('size',None)
    vendor = request.POST.get('vendor',None)
    products = Product.objects.filter(
        Q(productattribute__attribute_value__contains=request.POST.get('item_type'))&
        Q(productattribute__attribute_value__contains=request.POST.get('style'))&
        Q(productattribute__attribute_value__contains=request.POST.get('gender'))&
        Q(productattribute__attribute_value__contains=request.POST.get('colour'))&
        Q(productattribute__attribute_value__contains=request.POST.get('size'))
        ).distinct()
    if vendor:
        products = products.filter(vendor_id=vendor)
    product_attr = ProductAttribute.objects.filter(product_id__in=products.values('url'))
    product_img = ProductImage.objects.filter(product_id__in=products.values('url'))
    result = chain(products,product_attr,product_img)
    serialized_object = serializers.serialize('json', result)
    return HttpResponse(serialized_object, content_type='application/json')



@csrf_exempt
@require_http_methods(['POST', 'GET']) # only get and post
def crawl(request):
    """
    is_valid_url - Starts or gets status of a crawl request
    """
    # Post requests are for new crawling tasks
    if request.method == 'POST':

        url = request.POST.get('url', None) # take url comes from client. (From an input may be?)

        if not url:
            return JsonResponse({'error': 'Missing  args'})

        if not is_valid_url(url):
            return JsonResponse({'error': 'URL is invalid'})

        domain = urlparse(url).netloc # parse the url and extract the domain
        unique_id = str(uuid4()) # create a unique ID.

        # This is the custom settings for scrapy spider.
        # We can send anything we want to use it inside spiders and pipelines.
        # I mean, anything
        settings = {
            'unique_id': unique_id, # unique ID for each record for DB
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        # Here we schedule a new crawling task from scrapyd.
        # Notice that settings is a special argument name.
        # But we can pass other arguments, though.
        # This returns a ID which belongs and will be belong to this task
        # We are goint to use that to check task's status.
        # crawler_settings = get_project_settings()
        # print(crawler_settings)
        # crawler = CrawlerProcess(get_project_settings())
        # crawler.crawl(LoversSpider)
        #
        # crawler.start()
        task = SCRAPYD.schedule('default', 'review_products',
                                settings=settings, url=url, domain=domain)
        SCRAPYD.schedule('default', 'decjuba_products',
                         settings=settings, url=url, domain=domain)
        SCRAPYD.schedule('default', 'loverthelabel_products',
                         settings=settings, url=url, domain=domain)
        return JsonResponse({'status': 'started'})

    # Get requests are for getting result of a specific crawling task
    if request.method == 'GET':
        # We were passed these from past request above. Remember ?
        # They were trying to survive in client side.
        # Now they are here again, thankfully. <3
        # We passed them back to here to check the status of crawling
        # And if crawling is completed, we respond back with a crawled data.
        task_id = request.GET.get('task_id', None)
        unique_id = request.GET.get('unique_id', None)

        if not task_id or not unique_id:
            return JsonResponse({'error': 'Missing args'})

        # Here we check status of crawling that just started a few seconds ago.
        # If it is finished, we can query from database and get results
        # If it is not finished we can return active status
        # Possible results are -> pending, running, finished
        status = SCRAPYD.job_status('default', task_id)
        if status == 'finished':
            # this is the unique_id that we created even before crawling started.
            item = ScrapyItem.objects.get(unique_id=unique_id)
            return JsonResponse({'data': item.to_dict['data']})
        return JsonResponse({'status': status})
