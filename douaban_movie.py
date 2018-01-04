from bs4 import BeautifulSoup
import requests
import codecs

download_url = 'https://movie.douban.com/top250'
def download_page(download_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    # 取文本可用.text,取图片、文件可用.content
    data = requests.get(download_url, headers=headers).content
    return data

def parse_html(html):
    soup = BeautifulSoup(html,"lxml")
    movie_list = soup.find('ol', attrs={'class': 'grid_view'})
    #movie_list = soup.select(' div > div.info > div.hd > a > span')

    movie_name_list = []

    for movie_li in movie_list.find_all('li'):

        detail = movie_li.find('div', attrs={'class': 'hd'})
        movie_name = detail.find('span', attrs={'class': 'title'}).get_text()

        movie_name_list.append(movie_name)
    print(movie_name_list)
    next_page = soup.find('span', attrs={'class': 'next'}).find('a')
    if next_page:
        return movie_name_list, download_url + next_page['href']
    return movie_name_list, None

def main():
    url = download_url
    #filename =
    with codecs.open('movie', 'wb', encoding='utf-8') as fp:
        while url:
            html = download_page(url)
            movies, url = parse_html(html)
            fp.write(u'{movies}\n'.format(movies='\n'.join(movies)))
main()


