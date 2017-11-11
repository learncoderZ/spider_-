

import urllib.request
import requests
from bs4 import BeautifulSoup
import re
import pymongo

MONGO_URL='localhost'
MONGO_DB='TDE'
MONGO_TABLE='TED'

#MongoDB调用
client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]

#获取视频页码
def find_page():
    num = input("输入要选择的页码，1-72" )
    url_page = 'https://www.ted.com/talks?page=%s' %num
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    ted_page = requests.get(url_page, headers=headers).content
    soup = BeautifulSoup(ted_page,"html.parser")
    #视频详细页网址后缀
    cont = soup.findAll(attrs={"data-ga-context":"talks"})
    #视频名称及数量
    i = 0
    for n in cont:
        i = i + 1
        if i % 2 ==0:
            names = n['href'].split(r"/")
            #print(names)
            name = names[2].split("_")
            real_name = name[2:]
            fullname = ""
            for word in real_name:
                fullname = fullname + word + " "
            print("page:"+str(int(i/2))+" is "+fullname)
            print(" ")
    print("一共" + str(int(i / 2)) + "个视频")
    return cont
#find_page()
#选择要下载的视频
def choice():
    try:
        num = input("请输入1表示单个下载 输入2表示批量下载 输入3表示返回上一级重新选择---")
        if int(num) ==1:
            num = input("请输入要下载的页面 如有多个请用逗号分隔-36以内")
            pages = num.split(",")
            return pages


        elif int(num) == 2:
            num = input("请输入要下载的页面(36以内） 格式如下a-b,c-d")
            new_page = []
            pages = num.split(",")
            for page in pages:
                page2 = page.split("-")
                for _ in range(int(page2[0]), int(page2[1]) + 1):
                    new_page.append(_)
            return new_page
        elif int(num) == 3:
            find_page()
            choice()

        else:
            print("输入错误请重新输入")
            choice()
    except:
        print("输入错误请重新输入")
        choice()

download_url = ''
def download(conts, page):
    #全局变量
    global donwload_url
    #测试
    try:
        page = int(page)
    except:
        print("发现输入的编号有问题 请重新输入")
        choice()
    raw_url = conts[page * 2]['href']
    print("你要下载的页面是: " + raw_url)
    names = raw_url.split(r"/")
    name = names[2].split("_")
    real_name = name[2:]
    fullname = ""
    for x in real_name:
        fullname = fullname + x + "_"
    print("要下载的视频是: " + fullname)
    url = 'https://www.ted.com%s' % (raw_url)
    response = requests.get(url)
    cont = response.content
    soup = BeautifulSoup(cont, "html.parser")
    element = soup.findAll("script")
    patter = re.compile('http.*?mp4.apikey=.*?"')
    stre = patter.findall(str(element))
    for u in stre:
        if "64k" in u:
            u = u.split('"')
            download_url = u[0]
            print("获得下载地址: " + download_url)
            #mongeDB字典存储
            m = {
                'fullname': fullname,
                'url': url,
                'download_url': download_url
            }
            return m
    print(m)

# 把详情页面的url和标题（title)以及下载地址保存到mongo中
def save_to_mongo(m):
    if db[MONGO_TABLE].insert(m):
        print('存储到MongoDB成功', m)
        return True
    return False

# 把详情页面的url和标题（title)以及组图的地址list保存到local中
def save_to_local(m):
    print("开始下载")
    try:
        urllib.request.urlretrieve(m['download_url'], filename=fullname + ".mp4", reporthook=Schedule)
        print("下载完成")
    except:
        print("下载出现问题 重新下载")
        download(cont, page)

pre=0
def Schedule(a,b,c):
    global pre
    per = 100.0 * a * b / c
    if int(per)-pre>0:
        print('%.2f%%' % per)
        pre=int(per)
    #if pre=>100:
        #pre=0

if __name__ == '__main__':
    conts=find_page()
    pages=choice()
    print("你需要下载的内容编号一共是:")
    print(pages)
    select = input("请输入1表示储存至Monngo 输入2表示下载至本地 ---")
    if int(select) == 1:
        for page in pages:
            m = download(conts, page)
            save_to_mongo(m)
    elif int(select) == 2:
        for page in pages:
            m = download(conts, page)
            save_to_local(m)
