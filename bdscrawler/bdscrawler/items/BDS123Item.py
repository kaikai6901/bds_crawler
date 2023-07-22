import scrapy

from bdscrawler.basecrawler.items.BaseItem import BaseItem

class BDS123Item(BaseItem):
    price_unit = scrapy.Field()
    description = scrapy.Field()
    project = scrapy.Field()
    n_bedrooms = scrapy.Field()
    n_baths = scrapy.Field()
    author = scrapy.Field()
    last_time_in_page = scrapy.Field()
