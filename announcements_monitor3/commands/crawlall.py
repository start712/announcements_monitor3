#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 15:28:08 2018

@author: bobochj
"""

import sys
import os


from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerRunner
from scrapy.utils.conf import arglist_to_dict
from scrapy.exceptions import UsageError

import mysql_connecter as mysql_con

class Command(ScrapyCommand):
    requires_project = True

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-a", dest="spargs", action="append", default=[], metavar="NAME=VALUE",
                          help="set spider argument (may be repeated)")
        parser.add_option("-o", "--output", metavar="FILE",
                          help="dump scraped items into FILE (use - for stdout)")
        parser.add_option("-t", "--output-format", metavar="FORMAT",
                          help="format to use for dumping items with -o")

    def process_options(self, args, opts):
        ScrapyCommand.process_options(self, args, opts)
        try:
            opts.spargs = arglist_to_dict(opts.spargs)
        except ValueError:
            raise UsageError("Invalid -a value, use -a NAME=VALUE", print_help=False)
            
    def run(self, args, opts):
        # settings = get_project_settings()
        spider_loader = self.crawler_process.spider_loader
# =============================================================================
#         
#         spider_list = mysql_con.connect("SELECT spider_id FROM spider_list WHERE `type` = 'monitor'", host='localhost',user='spider',password = 'startspider', dbname = 'spider')
#         spider_list = [l0[0] for l0 in spider_list]
#         for spidername in args or spider_loader.list():
#             if spidername in spider_list:
#                 print("*********monitor spidername************" + spidername)
#                 self.crawler_process.crawl(spidername, **opts.spargs)
# =============================================================================
        spider_path = os.path.join(os.path.dirname(__file__), '..', r'spiders')
        spider_path = os.path.abspath(spider_path)
        spider_list = os.listdir(spider_path)
        spider_list = [os.path.splitext(s)[0] for s in spider_list]
        for spidername in spider_list or spider_loader.list():
            if spidername in ['__init__', '__pycache__']:
                continue
            print("*********monitor spidername************\n" + spidername)
            self.crawler_process.crawl(spidername, **opts.spargs)

        self.crawler_process.start()