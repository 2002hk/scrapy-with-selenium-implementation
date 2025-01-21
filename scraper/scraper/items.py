# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class SearchItem(scrapy.Item):
    ref=scrapy.Field()
    alt_red=scrapy.Field()
    app_recv=scrapy.Field()
    app_val=scrapy.Field()
    add=scrapy.Field()
    proposal=scrapy.Field()
    status=scrapy.Field()
    