from itemadapter import ItemAdapter
from bdscrawler.basecrawler.utils.helpers import *
from scrapy.exceptions import DropItem
class AlonhadatExtractAddress:
    def __init__(self):
        self.vocab = ['thành phố', 'tỉnh', 'quận', 'huyện', 'thị xã', 'xã', 'phường', 'thị trấn', 'đường', 'phố']

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('address'):
            address = adapter.get('address').strip().lower()
            for word in self.vocab:
                if word in address:                    address = address.replace(word, '')
            subdivision = address.split(',')
            province = subdivision[-1].strip().title()
            district = subdivision[-2].strip().title()
            commune = subdivision[-3].strip().title()
            if len(subdivision) > 3:
                full_street_name = subdivision[0].strip().title()
            else:
                full_street_name = ''
            adapter['province'] = province
            adapter['district'] = district
            adapter['commune'] = commune
            number, street_name = extract_words_with_numbers_and_remaining(full_street_name)
            adapter['street'] = {
                'full_street_name': full_street_name,
                'compound': {
                    'street_name': street_name,
                    'number': number
                }
            }
            adapter['compound'] = {
                'commune': commune,
                'district': district,
                'province': province
            }
        return item

class AlonhadatConvertPricePipline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('total_price'):
            s_price = get_format_string(adapter.get('total_price'))
            s_price = s_price.replace(',', '.')

            price = extract_float_number(s_price)
            if price is None:
                adapter['price_per_m2'] = 0
                adapter['total_price'] = 0
            else:
                price = price * convert_price_unit(s_price)

                if '/' in s_price:
                    price = price * adapter.get('square')

                adapter['price_per_m2'] = price / adapter.get('square')
                adapter['total_price'] = price
            return item
        else:

            raise DropItem(f"Missing price in {item}")


