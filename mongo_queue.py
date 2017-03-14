# -*- coding: utf-8 -*-

from pymongo import MongoClient, errors
from datetime import datetime

class MongoQueue:
    OUTSTANDING, PROCESSING, COMPLETE = range(3)

    def __init__(self, client=None, timeout=300):
        self.client = MongoClient() if client is None else client
        self.db = self.client.php_cache
        self.timeout = timeout

    def __nonzero__(self):
        record = self.db.crawl_queue.find_one(
            {'statue':{'$ne':self.COMPLETE}}
        )
        return True if record else False

    def push(self, url):
        try:
            self.db.crawl_queue.insert({'_id':url, 'statues':self.OUTSTANDING})
        except errors.DuplicateKeyError:
            pass

    def pop(self):
        record = self.db.crawl_queue.find_and_modify(
            query={'statues':self.OUTSTANDING},
            update={'$set':{'statues':self.PROCESSING, 'timestamp':datetime.now()}}
        )
        if record:
            return record['_id']
        else:
            self.repair()
            raise KeyError()

    def complete(self, url):
        self