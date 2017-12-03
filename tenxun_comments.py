# -*- coding: utf-8 -*-

#解析网页json文件，提取动态网页AJAX的url

import json
import requests
import re
import time
from datetime import datetime

header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}
#获取腾讯视频电视剧的网址
start_url = 'https://v.qq.com/x/cover/i5w51tl7vbl5mid.html'
getID_u = 'http://ncgi.video.qq.com/fcgi-bin/video_comment_id?otype=json&op=3&vid='
url = 'https://coral.qq.com/article/%s/comment?commentid=0&reqnum=10'

#获取vid的值
def get_vid(start_url):
    #得到网页源码
    html = requests.get(start_url, headers=header).content.decode('utf-8')
    #得到html中的vid值
    data = re.compile(r'class="item"\s*?id="(.*?)">', re.S)
    vids = re.findall(data, html)
    return vids

#通过vid值获取commend_id
def get_commend_url(vids):
    for i in range(0, len(vids)):
        vid = vids[i]
        print(i)
        print(vid)
        time.sleep(2)
        getID_url=getID_u+vid
        con_id_html = requests.get(getID_url, headers=header).content.decode('utf-8')
        comment_id = re.findall('comment_id":"(.*?)"', con_id_html,re.S)
        comment_id = comment_id[0]
        comm_url = url%(comment_id)
        print(comm_url)
        get_comment(comm_url)

#得到评论
def get_comment(comm_url):
    comment_js = requests.get(comm_url, headers=header).content.decode('utf-8')
    jsDict = json.loads(comment_js)
    jsdata = jsDict['data']
    comments = jsdata['commentid']
    print(comments)
    for each in comments:
        content = each['content']
        time = each['time']
        datatime = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S.%f')
        result = {
            "content": content,
            "time": datatime
        }
        print(result)
        #each['content'])

def main():
    vids = get_vid(start_url)
    get_commend_url(vids)

if __name__ == '__main__':
    main()
