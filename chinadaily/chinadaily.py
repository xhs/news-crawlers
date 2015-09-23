#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import pymongo
from pprint import pprint

def generate_path(entry, index):
    if index > 1:
        return '%s_%d.html' %(entry, index)
    else:
        return entry + '.html'

client = pymongo.MongoClient('localhost', 27017)
db = client.crawler
collection = db.chinadaily

base_url = 'http://www.chinadaily.com.cn/china/'
entries = ['hotonthweb', 'governmentandpolicy', 'society', 'scitech']

for entry in entries:
    for i in xrange(1, 101):
        try:
            page = requests.get(base_url + generate_path(entry, i))
            soup = BeautifulSoup(page.text, 'html.parser')

            articles = soup.find_all('div', class_='busBox1 lisSty')
            for article in articles:
                link = article.h3.a
                path = link['href']
                time = article.find_all('span', class_='mb10 block')[0]
                summary = article.p

                article_summary = summary.text
                article_timestamp = time.text[1:-1]
                article_title = link.text
                article_url = base_url + path

                if collection.find_one({'title': article_title}):
                    continue

                article_page = requests.get(article_url)
                article_soup = BeautifulSoup(article_page.text, 'html.parser')

                content = article_soup.find_all('div', id='Content')[0]
                paragraphs = content.find_all('p')
                article_content = '\n\n'.join([p.text for p in paragraphs])

                data = {
                    'title': article_title,
                    'url': article_url,
                    'timestamp': article_timestamp,
                    'summary': article_summary,
                    'content': article_content
                }
                pprint(data)
                collection.insert_one(data)
        except Exception, e:
            pass

client.close()
