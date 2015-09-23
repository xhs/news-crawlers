#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import pymongo
from pprint import pprint

def generate_path(entry, index):
    if index > 1:
        return '%s/page/%d/' %(entry, index)
    else:
        return entry + '/'

client = pymongo.MongoClient('localhost', 27017)
db = client.crawler
collection = db.japantimes

base_url = 'http://www.japantimes.co.jp/news/'
entries = ['national', 'asia-pacific', 'business', 'world', 'reference']

for entry in entries:
    for i in xrange(1, 201):
        try:
            page = requests.get(base_url + generate_path(entry, i))
            soup = BeautifulSoup(page.text, 'html.parser')

            articles = soup.find_all('article', class_='story')
            if i == 1:
                articles = articles[1:]

            for article in articles:
                article_timestamp = article.div.header.hgroup.h3.span.text
                link = article.div.header.hgroup.h1.a
                article_title = link.text
                article_url = link['href']
                article_summary = article.div.p.text

                if collection.find_one({'title': article_title}):
                    continue

                article_page = requests.get(article_url)
                article_soup = BeautifulSoup(article_page.text, 'html.parser')

                content = article_soup.find_all('div', class_='entry')[0]
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
