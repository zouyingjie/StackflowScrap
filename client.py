# -*- coding: utf-8 -*-
import random
import re
import time
from multiprocessing import Process, Pool
from datetime import timedelta

from urllib.error import URLError

from url_downloader import download
from url_exception import ManyRequestException
from url_manager import MongoCache
from url_parser import lxml_parse_stackover_flow_question_title, lxml_parse_stackoverflow_question_vote

import os

stackoverflow_url = "http://stackoverflow.com/"
question_likn_regex = '/questions/(.*)'


def link_crawler(name):

    print('Child process (%s)   %s will start.' % (name, os.getpid()))


    cacheClient = MongoCache(expires=timedelta(days=30))
    end_page = int(name) * 2000
    start_page = end_page - 1999
    for i in range(start_page, end_page + 1):
        pass
        try:
            if i % 100 == 0:
                time.sleep(8)
            time.sleep(2)
            url = "http://stackoverflow.com/questions/tagged/python?page=" + str(i) + "&sort=votes&pagesize=50"
            html = download(url)
            links = get_links(html)

            # 遍历所有链接, 获取有答案的链接,
            for link in links:
                # 获取到匹配的问题链接和标题
                if re.match(question_likn_regex, str(link)):
                    title = lxml_parse_stackover_flow_question_title(link, html)
                    vote = lxml_parse_stackoverflow_question_vote(link, html)
                    question_url = stackoverflow_url + link
                    if title is not None:
                        cacheClient.insert_stackoverflow_question(question_url, title)
                    if vote is not None:
                        cacheClient.add_stackoverflow_vote(vote, question_url)
        except TypeError as e:
            print(e, os.getpid())
            continue
        except ManyRequestException as e:
            time.sleep(60)
            continue
        except URLError as e:
            continue

        except Exception as e:
            print(e, os.getpid())
            continue


# 解析所有链接
def get_links(html):
    web_page_regex = re.compile('<a[^>]+href=["\'](.*?)["\'] class="question-hyperlink', re.IGNORECASE)
    return web_page_regex.findall(html)

#
if __name__ == '__main__':
    print('Parent process %s.' % os.getpid())

    pool = Pool(6)

    for i in range(1, 7):
        pool.apply_async(link_crawler, args=(i,))
    pool.close()
    pool.join()
    print('All subprocesses done.')

