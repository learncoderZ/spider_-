
from bs4 import BeautifulSoup
import requests
import codecs

url = 'http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea=020000&keyword=%E7%88%AC%E8%99%AB&lang=c&stype=2&fromType=1'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
def job_page(url):

    # 取文本可用.text,取图片、文件可用.content
    data = requests.get(url, headers=headers).text
    #print(data)
    return data

html = job_page(url)

def detail_url(html):
    soup = BeautifulSoup(html,"lxml")
    #movie_list = soup.find('ol', attrs={'class': 'grid_view'})
    job_links = soup.select(' #resultList > div > p > span > a')
    #print(job_list)
    #job_name_list = []
    for link in job_links:
        #由于链接地址标签在herf属性里，所以需要用get获取
        href = link.get("href")
        print(href)
        #get_detail_info(href)

def get_detail_info(url):
    wb_data = requests.get(url, headers = headers)

    #开始解析详情页数据
    soup = BeautifulSoup(wb_data.text, 'lxml')

    #获取名称
    company_names = soup.select(" div > div.cn > p.cname > a")

    #获取地址
    addresss = soup.select(" div.tCompany_main > div > div > p")

    #获取岗位名称
    job_names = soup.select(" div.tHeader.tHjob > div > div.cn > h1")

    #获取薪酬
    prices = soup.select(" div.tHeader.tHjob > div > div.cn > strong")

    #获取职位信息
    information_jobs = soup.select(" div.tCompany_main > div > div")

    #获取公司信息
    company_infos = soup.select("div.tCompany_main > div > div")

    for company_name, address, job_name, price, information_job, company_info in zip(company_names, addresss, job_names, prices, information_jobs, company_infos):
        # 从标签里面提取内容
        data = {
            "company_name": company_name.get_text(),
            "address": address.get_text().strip(),
            "job_name": job_name.get_text(),
            "price": price.get("src"),
            "information_job": information_job.get("src"),
            "company_info": company_info.get_text()

        }
        # "sex": get_lorder_sex(sex.get("class"))
        print(data)
        return data
get_detail_info("http://jobs.51job.com/shanghai-sjq/97839164.html?s=01&t=0")
