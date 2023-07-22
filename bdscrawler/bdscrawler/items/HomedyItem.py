import scrapy
from bdscrawler.basecrawler.items.BaseItem import *

class HomedyItem(BaseItem):
    author = scrapy.Field()
    contact = scrapy.Field()
    project = scrapy.Field()
    project_url = scrapy.Field()
    min_price = scrapy.Field()
    max_price = scrapy.Field()
    min_square = scrapy.Field()
    max_square = scrapy.Field()
    max_price_per_m2 = scrapy.Field()
    min_price_per_m2 = scrapy.Field()
    last_time_in_page = scrapy.Field()
    