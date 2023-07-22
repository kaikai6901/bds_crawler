
from itemadapter import ItemAdapter
from unidecode import unidecode
from scrapy.exceptions import DropItem
class BDS123ProcessAddressPipeline:
    def __init__(self):
        self.vocab = ['quận', 'huyện', 'thị xã']

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('address'):
            address = adapter.get('address').strip()
            if '-' in address:
                project, district = address.rsplit("-", 1)
            else:
                project = ''
                district = address
            project = project.strip()
            adapter['project'] = project
            district = district.strip().lower()
            for word in self.vocab:
                if word in district:
                    district = district.replace(word, '')
            district = district.strip().title()
            adapter['province'] = 'Hà Nội'
            adapter['district'] = district
            adapter['commune'] = ''
            adapter['compound'] = {
                'commune': adapter['commune'],
                'district': district,
                'province': 'Hà Nội'
            }
        else:
            raise DropItem(f'Item missing address')
        return item

class BDS123ProcessPricePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('total_price'):
            total_price = adapter.get('total_price').strip()
            total_price = unidecode(total_price).lower()
            if total_price == 'thoa thuan':
                total_price = 0
                adapter['total_price'] = 0
                return item

            total_price = float(total_price)

            price_unit = adapter.get('price_unit').strip().lower()
            price_unit = unidecode(price_unit)

            if 'trieu' in price_unit:
                total_price = total_price * 1e6
            elif 'ty' in price_unit:
                total_price = total_price * 1e9

            adapter['total_price'] = total_price

            if isinstance(adapter.get('square'), float) or isinstance(adapter.get('square'), int):
                adapter['price_per_m2'] = total_price / adapter.get('square')
        else:
            raise DropItem('Item missing price')

        return item

