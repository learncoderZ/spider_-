import urllib.request
import re
import urllib.parse

#处理标签的类
class Tool:
    # 去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    # 删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    # 把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    # 将表格制表<td>替换为\t
    replaceTD = re.compile('<td>')
    # 把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    # 将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    # 将其余标签剔除
    removeExtraTag = re.compile('<.*?>')

    def replace(self, x):
        #正则替换sub
        x = re.sub(self.removeImg, "", x)
        x = re.sub(self.removeAddr, "", x)
        x = re.sub(self.replaceLine, "\n", x)
        x = re.sub(self.replaceTD, "\t", x)
        x = re.sub(self.replacePara, "\n ", x)
        x = re.sub(self.replaceBR, "\n", x)
        x = re.sub(self.removeExtraTag, "", x)
        # strip()将前后多余内容删除
        return x.strip()



#百度贴吧爬虫
class BDTB:

    #c初始化参数，传入地址
    def __init__(self,baseUrl,seeLZ, floortag):
        #base链接地址
        self.baseUrl = baseUrl
        #是否只看楼主
        self.seeLZ = '?see_lz='+str(seeLZ)
        #HTML标签剔除工具类对象
        self.tool = Tool()
        #全局file变量，文件写入对象
        self.file = None
        #楼层编号，初始为1
        self.floor = 1
        #默认的标题
        self.defaulttitle = u'百度贴吧'
        #是否写入楼分隔符
        self.floortag = floortag


    #传入页码，获取该页代码
    def getpage(self,pagenum):
        try:
            url = self.baseUrl+ self.seeLZ +'&pn=' + str(pagenum)
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            #print(response)
            return response.read().decode('utf-8')
        except urllib.request.URLError as e:
            if hasattr(e, "reason"):
                print("Failed to link with百度贴吧. Reason", e.reason)
                return None
    #获取标题
    def gettitle(self,page):
        #page = self.getpage(1)
        pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>', re.S)
        result = re.search(pattern,page)
        if result:
            #print (result.group(1))
            return result.group(1).strip()
        else:
            return None

    #提取帖子的页数
    def getpagenum(self,page):
        #page = self.getpage(1)
        pattern = re.compile('<li class="l_reply_num".*?>.*?</span>.*?<span class=.*?>(.*?)</span>', re.S)
        result = re.search(pattern, page)
        if result:
            #print (result.group(1))
            return result.group(1).strip()
        else:
            return None

    #获取每一层楼的内容
    def getcontent(self,page):
        #page = self.getpage(1)
        pattern = re.compile('<div id="post_content_.*?>(.*?)</div>', re.S)
        items = re.findall(pattern,page)
        contents = []
        for item in items:
            #将文本进行去标签处理，同时在前后加入换行符
            content = "\n" + self.tool.replace(item) + "\n"
            contents.append(content.encode('utf-8'))
            #contents.append(content)
        return contents

            #print(item.strip())

    def setfiletitle(self,title):
        #如果标题不为None，则获取到标题
        if title is not None:
            self.file = open(title +".txt", "wb")
        else:
            self.file = open(self.defaulttitle+ ".txt","wb")

    def writedate(self,contents):
        #向文件写入每一楼的信息
        for item in contents:
            if self.floortag == '1':
                #楼之间的分隔符

                floorline = "\n" + str(self.floor)+"楼" + u"----------------------------------------------------------\n"
                self.file.write(floorline.encode('utf-8'))
            self.file.write(item)
            self.floor +=1

    def start(self):
        indexpage = self.getpage(1)
        pagenum = self.getpagenum(indexpage)
        title = self.gettitle(indexpage)
        self.setfiletitle(title)
        if pagenum ==None:
            print("URl失效，重试")
            return
        try:
            print("该帖子共有" +str(pagenum)+"页")
            for i in range(1, int(pagenum)+1):
                print("正在写入第" +str(i) +"页数据")
                page = self.getpage(i)
                contents = self.getcontent(page)
                self.writedate(contents)
        #未出现异常
        except IOError as e:
            print("写入异常，原因" + e.message)
        finally:
            print("写入任务完成")
        if self.file:
            self.file.close()


print("请输入帖子代号")
#baseUrl = 'http://tieba.baidu.com/p/' + str(input(u'http://tieba.baidu.com/p/'))
baseUrl = 'http://tieba.baidu.com/p/5345781494'
#bdtb = BDTB(baseUrl,1)
seeLZ = input("是否只获取楼主发言，是输入1，否输入0\n")
floortag = input("是否写入楼层信息，是输入1，否输入0\n")
bdtb = BDTB(baseUrl, seeLZ, floortag)
bdtb.start()
1







#bdtb.getpage(1)
#bdtb.gettitle()
#bdtb.getpagenum()
#bdtb.getcontent(bdtb.getpage(1))
