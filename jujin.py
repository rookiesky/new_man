from HttpPorxy import HttpPorxy
import json
from bs4 import BeautifulSoup
import time
import re

http = HttpPorxy()

cursor = "0"
article_id = []
api = 'https://w.vpsman.net/wp-admin/wordpress_post_api.php?action=save'
cate = ''

def payloadData(cate_id):
    global cursor
    payload = {'cate_id': cate_id,'cursor': cursor,'id_type': 2,'limit': 20,'sort_type': 200 }
    return json.dumps(payload)

def getArticleId(cate_id):
    global cursor,article_id
    api = 'https://api.juejin.cn/recommend_api/v1/article/recommend_cate_feed'
    headers = {'Content-Type':'application/json','origin':'https://juejin.cn','referer':'https://juejin.cn/'}
    payload = payloadData(cate_id=cate_id)
    response = http.post(url=api,data=payload,headers=headers)
    response = json.loads(response)
    if len(response['data']) <= 0:
        http.logger.error('get article link error')
        return False
    cursor = response['cursor']
    article_id = [item['article_id'] for item in response['data']]

def bodyFormat(soup,response):
    title = soup.find('h1',attrs={'class','article-title'}).text.replace('\n','').replace(' ','')
    create_time = soup.find('time',attrs={'class','time'}).get('title').replace(' GMT+0800 (China Standard Time)','')
    start = time.strptime(create_time,'%a %b %d %Y %H:%M:%S')
    create_time = time.strftime('%Y-%m-%d %H:%M:%S',start)
    body = soup.find('div',attrs={'class','markdown-body'})
    try:
        body.find('style').extract()
    except:
        pass
    try:
        for item in body.find_all('img'):
            item.attrs['src'] = item.get('data-src')
    except:
        pass
    tags = re.findall('tag_name:"(.*?)",',response,re.S)
    post_tags = ",".join(tags)
    return {'post_title':title,'tag':post_tags,'post_date':create_time,'post_content':str(body)}

def body():
    global article_id
    for item in article_id:
        url = 'https://juejin.cn/post/{}'.format(item)
        response = http.get(url=url)
        if response == False:
            continue
        soup = BeautifulSoup(response,'html.parser')
        try:
            data = bodyFormat(soup,response)
            data['post_category'] = cate
            response = http.post(url=api,data=data)
            http.logger.info('post success,title:{},response:{}'.format(data['post_title'],response))
        except Exception as e:
            http.logger.error('body format error,msg:{}'.format(e))
        soup = ''
        response = ''
        time.sleep(1)
    article_id = []

def main():
    url = [{'cate_id':'6809637767543259144','cate':'web前端'},{'cate_id':'6809637769959178254','cate':'编程语言'}]
    for i in range(0,520):
        cate = '编程语言'
        ret = getArticleId(cate_id='6809637769959178254')
        if ret == False:
            exit()
        if len(article_id) <= 0:
            http.logger.error('article id is empty')
            exit()
        body()
        http.logger.info('success page {}'.format(i))
        time.sleep(2)

def boot():
    url = [{'cate_id':'6809637767543259144','cate':'web前端'},{'cate_id':'6809637769959178254','cate':'编程语言'}]
    for item in url:
        cate = item['cate']
        ret = getArticleId(cate_id=item['cate_id'])
        if ret == False:
            exit()
        if len(article_id) <= 0:
            http.logger.error('article id is empty')
            exit()
        body()
        http.logger.info('success cate {}'.format(cate))
        time.sleep(2)

boot()