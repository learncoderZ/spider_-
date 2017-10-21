import json
import re
from hashlib import md5
import os
import requests
from urllib.parse import urlencode
import pymongo
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from json.decoder import JSONDecodeError
from config import *
from multiprocessing import Pool

#MongoDB调用
client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]

#获取索引页面的数据
def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': 3
    }

    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引出错')
        return None


def parse_page_index(html):
    try:
        #使用json.loads解析，提取详细页的url
        data = json.loads(html)
        #取出详细页的url
        if data and 'data' in data.keys():
            for item in data.get('data'):
                # 生成器
                yield item.get('article_url')
    except JSONDecodeError:
        pass

#获取详细页面的html代码
def get_page_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情出错', url)
        return None

# 解析详情页面并提取title, 和图片地址
def parse_page_detail(html, url):
    soup = BeautifulSoup(html, "lxml")
    title = soup.select('title')[0].get_text()
    print(title)
    images_pattern = re.compile(r'gallery: (.*?),\n')
    result = re.search(images_pattern, html)
    if result:
        print(result.group(1))
        # 将字符串转换为json对象
        data = json.loads(result.group(1))
        # print(data)
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images: download_image(image)
            # print(images)
            return {
                'title': title,
                'url': url,
                'images': images
            }

# 把详情页面的url和标题（title)以及组图的地址list保存到mongo中
def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到MongoDB成功', result)
        return True
    return False


def download_image(url):
    print('正在下载', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except RequestException:
        print('请求图片出错', url)
        return None


def save_image(content):
    #定义文件位置、文件名、格式
    file_path = '{0}/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main(offset):
    html = get_page_index(offset, KEYWORD)
    for url in parse_page_index(html):
        # print(url)
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            if result: save_to_mongo(result)
            # print(result)


if __name__ == "__main__":
    groups = [x * 20 for x in range(GROUP_START, GROUP_END + 1)]
    #开进程池
    pool = Pool()
    pool.map(main, groups)

