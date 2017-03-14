# -*- coding: utf-8 -*-
from urllib.error import URLError
from urllib.request import urlopen,Request

import time

from url_exception import ManyRequestException

'''
 链接爬取, 传递基础 url 以及匹配 html 中链接的正则, 获取到每个网页中
 链接, 转为完整的网址后存储进队列, 然后进行下载解析,
 直到获取整个网站的所有符合条件的url

 使用set保证下载的链接不会重复,

 解析每个网页的标题然后与对应的url一起存储到mongoDB 中作为全文检索的索引进行使用

 完成可以可以通过标题内容对数据进行检索

'''
def download(url, num_retries = 3):
    print("Downloading:", url)
    try:
        # 通过urlopen读取到网页html, 读到之后返回, 进行html界面的正则解析
        # 解析到html网页中的所有a超链接 然后获取到其中的链接内容来进行匹配
        # 获取到的连接与基本url组合为完成的url存入mongoDB
        # headers = {'User-agent': 'wswp'}
        request = Request(url)
        response = urlopen(request)
        if response.status == 429:
            raise ManyRequestException("Too many request, please sleep")
        # if response.status == 200:
        #     print("200")
        html = response.read().decode('utf-8').strip()
    except URLError as e:
        print('URLError', e)
        time.sleep(10)
        html = None
    except UnicodeDecodeError as e:
        print('Error', e)
        html = None
    except TimeoutError:
        time.sleep(1)
        return download(url, num_retries-1)
    return html