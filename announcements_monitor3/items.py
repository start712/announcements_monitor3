# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AnnouncementsMonitor3Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    monitor_id = scrapy.Field()
    monitor_title = scrapy.Field()
    monitor_key = scrapy.Field()
    monitor_date = scrapy.Field()
    monitor_url = scrapy.Field()
    monitor_extra = scrapy.Field()
    #monitor_re = scrapy.Field()
    monitor_city = scrapy.Field()
    # 土地信息表中的内容
    content_html = scrapy.Field()
    content_detail = scrapy.Field()

    parcel_status = scrapy.Field()
    
    data_save = scrapy.Field()