import scrapy

class BaseItem(scrapy.Item):
    news_id           = scrapy.Field()
    news_url = scrapy.Field()
    title        = scrapy.Field()
    square       = scrapy.Field()
    total_price        = scrapy.Field()
    price_per_m2 = scrapy.Field()
    address      = scrapy.Field()
    published_at = scrapy.Field()
    province = scrapy.Field()
    district = scrapy.Field()
    commune = scrapy.Field()
    street = scrapy.Field()
    compound = scrapy.Field()
    createdAt = scrapy.Field()
    updateAt = scrapy.Field()
    source = scrapy.Field()

    def __repr__(self):
        return ''