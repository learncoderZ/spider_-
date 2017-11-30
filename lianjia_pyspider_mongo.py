#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-30 09:39:44
# Project: lianjia

from pyspider.libs.base_handler import *
import pymongo
import csv

class Handler(BaseHandler):
    crawl_config = {
    }
    
    client = pymongo.MongoClient('localhost')
    db = client['zhufang']
    
    
    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://sh.lianjia.com/zufang/pudong', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('.js_fanglist_title').items():
            self.crawl(each.attr.href, callback=self.detail_page)
            
        next = response.doc('.house-lst-page-box > a').eq(-1).attr.href
        #body > div.wrapper > div.page-box.house-lst-page-box > a:nth-child(10)
        #body > div.wrapper > div.page-box.house-lst-page-box > a:nth-child(9).filter('#1')
        #body > div.wrapper > div.page-box.house-lst-page-box > a.on
        
        self.crawl(next, callback=self.index_page)

    @config(priority=2)
    def detail_page(self, response):
        url = response.url
        name = response.doc('h1').text()
        prices = response.doc('.price > div').text()
        house_type = response.doc('.room > div').text()
        ares = response.doc('.area > div').text()
        community_name = response.doc('.addrEllipsis > a').text()
        address = response.doc('p.addrEllipsis').text()
        link_name = response.doc('body > div.zf-top > div.cj-cun > div.content.forRent > div.brokerInfo > div > div.brokerName > a.name').text()
        tel = response.doc('.brokerInfoText > .phone').text()
        
        
        return {
            "url": url,
            "name": name,
            "prices": prices,
            "house_type": house_type,
            "ares": ares,
            "community_name": community_name,
            "address": address,
            "link_name": link_name,
            "tel": tel
        }
    def on_result(self,result):
        if result:
            self.save_to_mongo(result)
            
    
    def save_to_mongo(self,result):
        if self.db['zhufang'].insert(result):
            print('save to mongo',result)
        
