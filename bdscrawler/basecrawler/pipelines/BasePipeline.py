import scrapy
from itemadapter import ItemAdapter
from datetime import datetime
from scrapy.exceptions import DropItem
from pymongo.errors import DuplicateKeyError
class SavingToDatabasePipeline(object):
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        required_fields = ['news_id', 'news_url', 'published_at', 'address', 'total_price', 'square', 'price_per_m2']

        for field in required_fields:
            if field not in adapter:
                raise DropItem('Item missing field')

        adapter['createdAt'] = datetime.now()
        adapter['updateAt'] = adapter['createdAt']
        if not adapter.get('last_time_in_page'):
            adapter['last_time_in_page'] = adapter.get('published_at')
        news_id = adapter['news_id']
        if not news_id.startswith(spider.spider_code):
            adapter['news_id'] = spider.spider_code + news_id
        try:
            spider.collection.insert_one(adapter.asdict())
            print(f"Item {adapter.get('news_id')} success")
        except DuplicateKeyError:
            print(f"Item {adapter.get('news_id')} have already in database")
        except Exception as e:
            print(f"Item {adapter.get('news_id')} error when upload to database")
            raise DropItem
        return item
