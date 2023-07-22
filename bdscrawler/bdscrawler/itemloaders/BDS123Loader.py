from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from bdscrawler.bdscrawler.utils.BDS123Helpers import *
from bdscrawler.basecrawler.utils.helpers import convert_time


class BDS123ItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    published_at_in = MapCompose(lambda x: convert_time(x))
    last_time_in_page_in = MapCompose(lambda x: convert_time(x))
    n_bedrooms_in = MapCompose(lambda x: int(x.strip().split()[0]) if x else None)
    n_baths_in = MapCompose(lambda x: int(x.strip().split()[0]) if x else None)
    square_in = MapCompose(lambda x: float(x.strip().split()[0]) if x else None)
    author_in = MapCompose(lambda x: x.strip() if x else None)