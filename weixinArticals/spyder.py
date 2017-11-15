from urllib.parse import urlencode
from pyquery import PyQuery as pq
import requests
from requests.exceptions import ConnectionError
import pymongo
from config import *
base_url = 'http://weixin.sogou.com/weixin?'

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]
#注意cookies有效期
headers = {
    'Cookie':'CXID=D2C26BF3A834FF761932450A8578E2B3; ad=flllllllll2BTQh0lllllVoR987lllllHuTZskllll9llllljVxlw@@@@@@@@@@@; SUID=BEF06DB64D238B0A59DD6CA300045A26; IPLOC=CN3601; SUV=1510472988752465; ABTEST=4|1510472997|v1; SNUID=CD118B69DFDA821BB9A60100DFA13F98; weixinIndexVisited=1; ppinf=5|1510473061|1511682661|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxOlp8Y3J0OjEwOjE1MTA0NzMwNjF8cmVmbmljazoxOlp8dXNlcmlkOjQ0Om85dDJsdUxmZlc5a0FqaE9NSFRRc3pYLU5vOXNAd2VpeGluLnNvaHUuY29tfA; pprdig=e5hSiqlDa0NcxeTjuDDMjr0fYBXNY3Ti97dacI-OnhchT5AvFWr78cG56U_2LAxlHZ3fIPVQM4G6AJiHd2qgz0ZFr9z66aXVaZ3y3ZNt9mJ6KgBXvfjiM5k7RPvb058b0A6mmcUhOM2FRSDpuJHCwpi4wag9G5PKqe3kysTfd2U; sgid=30-31939897-AVoHicWXfEtntV0icBc0Czgcw; ppmdig=1510665831000000662682cc9ed790754f7b8138c59b3fa6; JSESSIONID=aaauk7CSRAyQW59snKv8v; sct=5',
    'Host':'weixin.sogou.com',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'

}


proxy =None
max_count = 5

def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code ==200:
            return response.text
        return None
    except ConnectionError:
        return None

def get_html(url, count=1):
    print('Crawling', url)
    print('Trying count', count)
    global proxy
    if count>= max_count:
        print('Tried too many counts')
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(url, headers=headers, proxies=proxies, allow_redirects=False)
        else:
            response = requests.get(url, headers=headers, allow_redirects=False)
        if response.status_code ==200:
            print('200')
            return response.text
        if response.status_code ==302:
            #need proxy
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using Proxy', proxy)
                return get_html(url)
            else:
                print('Get proxy Failed')
                return None
    except ConnectionError as e:
        print('Error Occurred', e.args)
        proxy = get_proxy()
        count +=1
        return get_html(url, count)

def get_index(keyword, page):
    data ={
        'query': keyword,
        'type': 2,
        'page': page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html

def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')

def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def parse_detail(html):
    doc = pq(html)
    title = doc('.rich_media_title').text()
    content = doc('.rich_media_content ').text()
    data = doc('#post-date').text()
    nickname = doc('#meta_content > span').text()
    #wechat =
    return {
        'title': title,
        'content': content,
        'data': data,
        'nickname': nickname
    }

def save_to_mongo(data):
    #插入、更新、去重
    if db['articles'].update({'title': data['title']}, {'$set': data}, True):
        print('Saved to Mongo', data['title'])
    else:
        print('Saved to Mongo Failed', data['title'])

def main():
    for page in range(1,101):
        html = get_index(KEYWORD,page)
        if html:
            article_urls = parse_index(html)
            for artical_url in article_urls:
                artical_html = get_detail(artical_url)
                if artical_html:
                    artical_data = parse_detail(artical_html)
                    print(artical_data)
                    save_to_mongo(artical_data)
        #print(html)
if __name__ == '__main__':
    main()

