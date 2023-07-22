from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.loader import ItemLoader
from bdscrawler.basecrawler.utils.helpers import *


class ALonhadatItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    width_in = MapCompose(lambda x: None if '-' in x else extract_float_number(x))
    length_in = MapCompose(lambda x: None if '-' in x else extract_float_number(x))
    n_floors_in = MapCompose(lambda x: extract_float_number(x))
    n_bedrooms_in = MapCompose(lambda x: extract_float_number(x))
    published_at_in = MapCompose(lambda x: convert_time(x))
    n_dinning_rooms_in = MapCompose(lambda x: 1 if x == 'nan' else 0)
    kitchen_in = MapCompose(lambda x: 1 if x == 'nan' else 0)
    balcony_in = MapCompose(lambda x: 1 if x == 'nan' else 0)
    parking_lot_in = MapCompose(lambda x: 1 if x == 'nan' else 0)
    owner_in = MapCompose(lambda x: 1 if x == 'nan' else 0)
    project_in = MapCompose(lambda x: x.replace('(xem chi tiết dự án)', '').strip())
    square_in = MapCompose(lambda x: extract_float_number(x))
    contact_out = Join()

