#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 17:23:54 2018

@author: bobochj
"""

import scrapy
import announcements_monitor3.items
import re
import pandas as pd
import numpy as np
import json
import datetime

class Spider(scrapy.Spider):
    name = "江苏土地市场网"

    def start_requests(self):
        url0 = 'http://www.landjs.com/web/ggdk_list.aspx?type=&xzq='
        district = range(3201, 3214)
        for i in district:
            url = url0 + str(i)
            yield scrapy.Request(url=url, callback=self.url_parse)
    
    def url_parse(self, response):
        sel = scrapy.Selector(response)
        sel = sel.xpath('//*[@id="AspNetPager1"]/div[1]/text()')[0]
        page_num = sel.extract().split('/')[-1].strip()
        for i in range(1, int(page_num)+2):
            url = response.url + '&page=' + str(i)
            yield scrapy.Request(url=url, callback=self.catalog_parse)

    def catalog_parse(self, response):
        # 用正则表达式解析网页
        html = response.text
        
        no_data_re = "class='thc'"
        if not re.search(no_data_re, html):
            # find all rows of the table
            tr_re = '<tr class="dg_item">.+?</tr>|<tr class="dg_alter">.+?</tr>'
            e_trs = re.findall(tr_re, html, re.S)
            for e_tr in e_trs:
                # 定义一些常规变量
                item = announcements_monitor3.items.AnnouncementsMonitor3Item()
                item['monitor_city'] = ''
                item['monitor_id'] = self.name
    
                data_re = '<td.+?>(.+?)</td>'
                data_list = re.findall(data_re, e_tr, re.S)
                #data_list = [data_list[i] for i in range(len(data_list)) if i%2==1]
                item['monitor_date'] = data_list[6]
                item['data_save'] = {
                        '行政区': data_list[1]
                        , '宗地位置': data_list[3]
                        , '土地用途': data_list[4]
                        , '面积': data_list[5]
                        , '公告开始时间': data_list[6]
                        }
    
                a_re = '<a href=\'(.+?)\' target=\'_blank\'>'
                url = 'http://www.landjs.com/web/' + \
                       re.search(a_re, data_list[2]).group(1)
                yield scrapy.Request(url=url
                                     , meta={'item':item}
                                     , callback=self.detail_parse)
    
    def detail_parse(self, response):
        # parse the detail page
        item = response.meta['item'].copy()
        sel = scrapy.Selector(response)
        root_path = r'//*[@id="form1"]/table[6]/tbody/tr/td/table[3]'
        sites = sel.xpath(root_path)
        """在使用chrome等浏览器自带的提取extract xpath路径的时候,
           通常现在的浏览器都会对html文本进行一定的规范化,
           导致明明在浏览器中提取正确, 却在程序中返回错误的结果"""
        if not sites:
            sites = sel.xpath(root_path.replace("/tbody",""))
        table = sites[0]
        html = table.extract()
        df = pd.read_html(html)[0]
        ndarr = np.array(df)
        ndarr = ndarr.reshape(-1,2)
        ser = pd.Series(ndarr[:,1], index=ndarr[:,0])
        ser = ser.loc[ser.index.notna()]
        #ser['url'] = response.url
        item['monitor_url'] = response.url
        item['monitor_city'] = self.name
        item['monitor_title'] = (ser['公告编号'] if pd.notna(ser['公告编号']) 
                                else '[网页编号]'+response.url.split('=')[-1])\
                                + ser['公告地块编号']
        if "挂牌截止时间" in ser and pd.notna(ser["挂牌截止时间"]):
            date0 = pd.to_datetime(ser["挂牌截止时间"], errors='coerce')
            item['parcel_status'] = 'onsell' if date0 > datetime.datetime.now() \
                                    else 'sold'
        item['content_detail'] = ser

        item['monitor_extra'] = item['data_save']
        item['monitor_extra']['files'] = {}
        file_str_list = ['lblcrwj', 'lblcrxz', 'lblxct', 'lblfj']
        for s in file_str_list:
            e_span = table.xpath('//*[@id="{}"]/text()'.format(s))[0]
            """[<Selector xpath='//*[@id="lblcrwj"]/text()' data='无'>]"""
            if e_span.extract() == '无':
                continue
            e_as_href = table.xpath('//*[@id="{}"]/a/@href'.format(s))
            e_as_href = ['http://www.landjs.com/web/' + s.extract() for s in e_as_href]
            e_as_text = table.xpath('//*[@id="{}"]/a/text()'.format(s))
            e_as_text = [s.extract().strip() for s in e_as_text]
            file_dict = dict(zip(e_as_text, e_as_href))
            item['monitor_extra']['files'].update(file_dict)
            
        item['monitor_extra'] = json.dumps(item['monitor_extra'], ensure_ascii=False)
        yield item