"""
Models - Contains all the django models used in the app
"""
import json
from django.db import models
from django.utils import timezone
# Create your models here.

class ScrapyItem(models.Model):
    """
    Represents a single product
    """
    unique_id = models.CharField(max_length=100, null=True)
    name = models.TextField() # this stands for our crawled data
    date = models.DateTimeField(default=timezone.now)


    @property
    def to_dict(self):
        """
        This is for basic and custom serialisation to return it to client as a JSON.
        """
        name = {
            'name': json.loads(self.name),
            'date': self.date
        }
        return name

    def __str__(self):
        return self.unique_id


class ProductVendor(models.Model):
    """
    Represents a single store/location
    """
    name = models.TextField()
    address = models.TextField()
    geolocation = models.TextField()

    @property
    def __str__(self):
        return self.pk


class Product(models.Model):
    """
    Represents a single product
    """
    name = models.TextField()
    url = models.TextField(primary_key=True)
    vendor = models.ForeignKey(ProductVendor,
                               on_delete=models.CASCADE, null=True)
    stock = models.BooleanField(default=True)

    @property
    def __str__(self):
        return self.pk
        def to_dict(self):
            data = {
                'name':self.name,
                'url':self.url,
                'vendor_id':self.vendor,
                'stock':self.stock
            }

class ProductImage(models.Model):
    """
    Represents a single image
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='url', null=True)
    image_url = models.TextField(primary_key=True, default='default')



class Attribute(models.Model):
    """
    Represents a single type of attribute
    """
    name = models.TextField(null=True)

    @property
    def __str__(self):
        return self.pk

class ProductAttribute(models.Model):
    """
    Represents a single attribute of a product ProductVariant
    """
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE, to_field='url', null=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    attribute_value = models.TextField(null=True)

    @property
    def __str__(self):
        return self.pk
