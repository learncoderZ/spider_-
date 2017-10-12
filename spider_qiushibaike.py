import urllib.request
import re
import urllib.parse
import time

#糗事百科爬虫类
class QSBK:
    #初始化方法，定义一些类
    def __init__(self):
        self.pageIndex = 1
        #初始化headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
            }
        #存放段子的变量，每个元素是每一页的段子
        self.stories = []
        #存放程序是否继续运行的变量
        self.enable = False
    #传入某一页的索引获得页面代码
    def getpage(self, pageIndex):
        try:
            url = 'https://www.qiushibaike.com/8hr/page/' + str(pageIndex)
            #构建请求的request
            request = urllib.request.Request(url, headers=self.headers)
            #利用urlopen获取页面代码
            response =urllib.request.urlopen(request)
            #将页面转化为UTF—8编码
            pagecode = response.read().decode('utf-8')
            return pagecode
        except urllib.request.URLError as e:
            if hasattr(e, 'reason'):
                print("Failed to link with qiushibaike.com. Reason", e.reason)
                return None

    #传入某一页页码，返回本页不带图的段子列表
    def getpageItem(self,pageIdex):
        pagecode = self.getpage(pageIdex)
        if not pagecode:
            print("页面加载失败...")
            return None
        pattern = re.compile('<div.*?author clearfix">.*?h2>(.*?)</h2>.*?span>(.*?)</span>.*?stats-vote.*?class.*?>(.*?)</i>.*?stats-comments.*?class="number".*?>(.*?)</i>.*?</div>', re.S)
        items = re.findall(pattern,pagecode)
        #用来存储每页的段子
        pagestories = []
        #遍历正则表达式匹配的信息
        for item in items:
            #是否含有图片
            # print(len(item))
            haveImg = re.search('thumb', item[2])
            # item[0]: 段子发布者     item[1]：段子内容
            # item[2]: 判断段子是否包含图片    item[3]: 点赞数    item[4]: 评论数
            if not haveImg:
                replace = re.compile('<br/>')
                text = re.sub(replace, "\n", item[1])
                span = re.compile('<span>')
                text = re.sub(span, '    ', text)
                span = re.compile('</span>')
                text = re.sub(span, '\n', text)

                pagestories.append([item[0].strip(),text.strip(), item[2], item[3]])
        return pagestories

    #加载并提取页面的内容，加入到列表中
    def loadpage(self):
        if self.enable == True:
            if len(self.stories) < 2:
                #获取新一页
                pagestories = self.getpageItem(self.pageIndex)
                #将该页的段子存放到全局list中
                if pagestories:
                    self.stories.append(pagestories)
                    #获取完后页码加一，读取下一页
                    self.pageIndex +=1

    #调用方法，每次敲回车打印输出一个段子
    def getonestory(self, pagestories, page):
        #遍历一页段子
        for story in pagestories:
            #等待用户输入
            Input = input()
            #每当输入回车一次，判断一下是否要加载新页面
            self.loadpage()
            #如果输入q则程序结束
            if Input == 'Q':
                self.enable = False
                return

            print(u'第%d页\t发布人:%s\t赞:%s\t评论:%s\n%s' % (page, story[0], story[2], story[3], story[1]))

    #开始方法
    def start(self):
        print("正在读取糗事百科，按回车查看新段子， Q退出")
        #是变量为True，程序可正常运行
        self.enable = True
        #先加载一页内容
        self.loadpage()
        #局部变量，控制当前读到了第几页
        nowpage = 0
        while self.enable:
            if len(self.stories) > 0:
                pagestories = self.stories[0]
                nowpage +=1
                del self.stories[0]
                self.getonestory(pagestories,nowpage)

spider = QSBK()
spider.start()
