# -*- coding: utf-8 -*-

import zlib
import pickle
from bson.binary import Binary
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.cursor import Cursor
from datetime import datetime, timedelta

'''
URL管理器

使用MongoDB来缓存已经爬取过的 url 和发生错误的 url 避免重复爬取
同时用来检索相关数据

'''

class MongoCache:
    def __init__(self, client=None, expires=timedelta(days=30)):

        # 创建缓存数据库以及存储集合
        self.client = MongoClient('localhost', 27017) if client is None else client
        # 获取缓存数据库
        self.db = self.client.cache
        try:
            self.db.errorpage.create_index('timestamp', expiresAfterSeconds=expires.total_seconds())
            self.db.webpage.create_index('timestamp', expiresAfterSeconds=expires.total_seconds())
            self.db.title_document.ensure_index([('title', 'text'),],)
            self.db.stackover_flow.create_index([('title', 'text'),],)
        except OperationFailure:
            pass

    '''
    添加与获取正常爬取网页
    '''

    def set_normal_page(self, url, result):
        record = {'result': Binary(zlib.compress(pickle.dumps(result))), 'timestamp': datetime.utcnow()}
        self.db.webpage.update({'_id': url}, {'$set': record}, upsert=True)

    def get_normal_page(self, url):
        record = self.db.webpage.find_one({'_id': url})
        if record:
            return pickle.loads(zlib.decompress(record['result']))
        else:
            return None

    '''
    添加与获取错误网页
    '''

    def set_error_page(self, url):
        record = {'result': url, 'timestamp': datetime.utcnow()}
        self.db.errorpage.update({'_id': url}, {'$set': record}, upsert=True)

    def get_error_page(self, url):
        record = self.db.errorpage.find_one({'_id': url})
        if record:
            return record['result']
        else:
            return None

    '''
    添加标题与url链接
    '''

    def set_title(self, title, url):
        self.db.title_document.insert_one({"title": title, "url": url})
        # self.db.title.update({"_id": title},{'$set':url}, upsert=True)
    def add_stackoverflow_vote(self, vote, url):
        record = {"vote": vote}
        self.db.stackover_flow.update({"url":url}, {"$set":record}, upsert=True)


    '''
    通过title或者url进行匹配查询
    '''
    def get_url_by_title(self, title):
        result = self.db.title_document.find_one({"title": title})
        return result

    def get_title_by_url(self, url):
        result = self.db.title_document.find_one({"url": url})
        return result

    '''
    通过输入信息进行文本检索
    '''
    def find_with_text_search(self, info):
       cursor =  self.db.title_document.find({ '$text': { '$search': info } },)
       for i in range(cursor.count()):
           print(cursor.__getitem__(i))

    def insert_stackoverflow_question(self, url, title):
        self.db.stackover_flow.insert_one({"title":title, "url":url})


cacheClient = MongoCache(expires=timedelta(days=30))