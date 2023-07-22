from itemadapter import ItemAdapter
from unidecode import unidecode
from bdscrawler.basecrawler.utils.helpers import *
from scrapy.exceptions import DropItem
from datetime import datetime
from pymongo.errors import DuplicateKeyError

def find_address_name(string, keywords):
    for keyword in keywords:
        if keyword in string:
            words = string.split(keyword)
            return words[-1].strip()
    return ''

class HomedyExtractAddress:
    def __init__(self):
        self.keyword = {
            'province' : ['thành phố', 'tỉnh'],
            'district' : ['quận', 'huyện', 'thị xã'],
            'commune' : ['xã', 'phường', 'thị trấn'],
            'street' : ['đường', 'phố', 'ngõ', 'ngách', 'hẻm']
        }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('address'):
            address = adapter.get('address').strip().lower()
            division = address.split(',')
            adapter['commune'] = ''
            adapter['district'] = ''
            adapter['province'] = ''
            adapter['street'] = ''
            for subdivision in division:
                name = subdivision.strip().lower()
                for key, value in self.keyword.items():
                    s = find_address_name(name, value).title()
                    if s != '':
                        adapter[key] = find_address_name(name, value).title()
            if adapter['province'] == '':
                adapter['province'] = division[-1].title()

            adapter['compound'] = {
                'commune': adapter['commune'],
                'district': adapter['district'],
                'province': adapter['province']
            }
        return item

class HomedyConvertPricePipline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('total_price'):
            s_price = unidecode(adapter.get('total_price')).strip().lower()
            s_price = s_price.replace(',', '.')

            s_square = unidecode(adapter.get('square')).strip().lower()

            price_unit = convert_price_unit(s_price)

            range_price = s_price.split('-')

            price = None

            if len(range_price) == 1:
                price = extract_float_number(s_price)
                if price is None:
                    price = 0
                price = price * price_unit
                min_price = price
                max_price = price
            else:
                price = extract_float_number(range_price[0])
                price = price * price_unit
                min_price = price
                max_price = extract_float_number(range_price[1]) * price_unit

            range_square = s_square.split('-')
            if len(range_square) == 1:
                square = extract_float_number(s_square)
                min_square = square
                max_square = square
            else:
                square = extract_float_number(range_square[0])
                min_square = square
                max_square = extract_float_number(range_square[1])

            if adapter.get('price_per_m2') is not None:

                s_price_per_m2 = unidecode(adapter.get('price_per_m2')).strip().lower()
                s_price_per_m2 = s_price_per_m2.replace(',', '.')

                price_unit = convert_price_unit(s_price_per_m2)

                range_price_per_m2 = s_price_per_m2.split('-')

                if len(range_price_per_m2) == 1:
                    price_per_m2 = extract_float_number(s_price_per_m2)
                    if price_per_m2 is None:
                        price_per_m2 = 0
                    price_per_m2 = price_per_m2 * price_unit
                    min_price_per_m2 = price_per_m2
                    max_price_per_m2 = price_per_m2
                else:
                    price_per_m2 = extract_float_number(range_price_per_m2[0])
                    price_per_m2 = price_per_m2 * price_unit
                    min_price_per_m2 = price_per_m2
                    max_price_per_m2 = extract_float_number(range_price_per_m2[1]) * price_unit
            else:
                price_per_m2 = price / square
                min_price_per_m2 = min_price / min_square
                max_price_per_m2 = max_price / max_square

            adapter['total_price'] = price
            adapter['min_price'] = min_price
            adapter['max_price'] = max_price
            adapter['square'] = square
            adapter['min_square'] = min_square
            adapter['max_square'] = max_square
            adapter['price_per_m2'] = price_per_m2
            adapter['max_price_per_m2'] = max_price_per_m2
            adapter['min_price_per_m2'] = min_price_per_m2

            return item
        else:
            raise DropItem(f"Missing price in {item}")
    




