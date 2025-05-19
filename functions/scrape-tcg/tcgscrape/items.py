# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CardItems(scrapy.Item):
    card_id = scrapy.Field()
    timestamp = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    company = scrapy.Field()
    tcg_name = scrapy.Field()
    set_name = scrapy.Field()
    image_src = scrapy.Field()
