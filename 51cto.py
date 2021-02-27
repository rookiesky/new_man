from HttpPorxy import HttpPorxy
from bs4 import BeautifulSoup
import time

http = HttpPorxy()
list_link = []
cate = ''
api_url = 'https://w.vpsman.net/wp-admin/wordpress_post_api.php?action=save'

def getListLink(url):
    global list_link
    response = http.get(url=url)
    if response == False:
        return False

    soup = BeautifulSoup(response,'html.parser')
    list_url = soup.find_all('a',attrs={'class','tit'})
    list_link = [item.get('href') for item in list_url]
    list_url = []

def bodyFormat(soup):
    title = soup.find('h1',attrs={'class','artical-title'}).text
    create_time = soup.find('a',attrs={'class','time fr'}).text
    body = soup.find('div',attrs={'class','editor-preview-side'})
    try:
        body.find('blockquote').extract()
    except:
        pass
    post_tag = ''
    try:
        tags = soup.find('div',attrs={'class','for-tag mt26'})
        
        for item in tags.find_all('a'):       
            if item.has_attr('class') == True and item['class'][0] == 'last':
                item.extract()
                continue
            post_tag += item.text + ','
        
        if len(post_tag) > 0:
            post_tag = post_tag.rstrip(',')
    except:
        pass
    return {'post_title':title,'tag':post_tag,'post_date':create_time,'post_content':str(body)}

def body():
    global list_link
    for url in list_link:
        response = http.get(url=url)
        if response == False:
            continue

        soup = BeautifulSoup(response,'html.parser')
        try:
            data = bodyFormat(soup)
            data['post_category'] = cate
            response = http.post(url=api_url,data=data)
            http.logger.info('Success title:{},response:{}'.format(data['post_title'],response.strip()))
            data = ''
        except Exception as e:
            http.logger.error('body format error,msg:{}'.format(e))
        soup = ''
        response = ''
        time.sleep(1)
    list_link = []

def main():
    global cate,list_link
    urls = {
       '编程语言':'https://blog.51cto.com/original/31',
       'Web前端':'https://blog.51cto.com/original/30',
       'linux教程':'https://blog.51cto.com/original/27' 
    }
    for key,url in urls.items():
        cate = key
        getListLink(url=url)
        if len(list_link) <= 0:
            http.logger.error('list link empty')
            continue
        body()
        http.logger.info('success,cate:{}'.format(cate))
        time.sleep(2)

main()