from selenium import webdriver
import time
from bs4 import BeautifulSoup

driver = webdriver.PhantomJS(executable_path = r'C:\Users\PT\Anaconda3\Scripts\phantomjs')
driver.get("http://pythonscraping.com/pages/javascript/ajaxDemo.html")
time.sleep(3)

#can
"""
print(driver.find_element_by_id('content').text)
driver.close()
"""
#or
pagesource = driver.page_source
bsobj = BeautifulSoup(pagesource,"lxml")
print(bsobj.find(id="content").get_text())
