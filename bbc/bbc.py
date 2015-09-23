#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import pymongo
from pprint import pprint
import string

def generate_path(query, page):
    return 'search/more?page=%d&q=%s&filter=news&suggid=' %(page, query)

base_url = 'http://www.bbc.co.uk/'
queries = [c for c in string.lowercase]
queries.extend([str(n) for n in range(0, 10)])

client = pymongo.MongoClient('localhost', 27017)
db = client.crawler
collection = db.bbc

for query in queries:
    for page in xrange(1, 201):
        try:
            page = requests.get(base_url + generate_path(query, page))
            soup = BeautifulSoup(page.text, 'html.parser')

            articles = soup.find_all('article')
            for article in articles:
                link = article.div.h1.a
                summary = article.find_all('p', class_='summary long')[0]

                article_timestamp = article.aside.dl.dd.time.text.strip()
                article_title = link.text
                article_url = link['href']
                article_summary = summary.text

                if collection.find_one({'title': article_title}):
                    continue

                article_page = requests.get(article_url)
                article_soup = BeautifulSoup(article_page.text, 'html.parser')

                content = article_soup.find_all('div', class_='story-body')[0]
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
