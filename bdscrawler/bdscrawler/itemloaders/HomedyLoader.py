from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.loader import ItemLoader
from bdscrawler.basecrawler.utils.helpers import *
import datetime

class HomedyItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    address_out = Join(",")
    total_price_out = Join()
    price_per_m2_out = Join()
    published_at_in = MapCompose(lambda x: convert_time(x))

