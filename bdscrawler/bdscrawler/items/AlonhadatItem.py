import scrapy

from bdscrawler.basecrawler.items.BaseItem import BaseItem

class AlonhadatItem(BaseItem):
    author = scrapy.Field()
    contact = scrapy.Field()
    description = scrapy.Field()
    project = scrapy.Field()
    project_url = scrapy.Field()
    length = scrapy.Field()
    width = scrapy.Field()
    n_floors = scrapy.Field()
    n_bedrooms = scrapy.Field()
    n_dinning_rooms = scrapy.Field()
    kitchen = scrapy.Field()
    balcony = scrapy.Field()
    parking_lot = scrapy.Field()
    license = scrapy.Field()
    front_road = scrapy.Field()
    direction = scrapy.Field()
    owner = scrapy.Field()
    last_time_in_page = scrapy.Field()