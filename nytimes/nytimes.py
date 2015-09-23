#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import pymongo
from pprint import pprint
import json

def generate_path(page):
    return 'pages/%d' %(page)

base_url = 'http://localhost:9999/'

client = pymongo.MongoClient('localhost', 27017)
db = client.crawler
collection = db.nytimes

for i in xrange(1, 1001):
    try:
        page = requests.get(base_url + generate_path(i), timeout=45.0)
        entries = json.loads(page.text)['entries']
        
        for entry in entries:
            if collection.find_one({'title': entry['title']}):
                continue

            article_page = requests.get(entry['url'])
            article_soup = BeautifulSoup(article_page.text, 'html.parser')

            content = article_soup.find_all('div', class_='story-body')[0]
            paragraphs = content.find_all('p', class_='story-body-text')
            article_content = '\n\n'.join([p.text for p in paragraphs])

            entry['content'] = article_content
            pprint(entry)
            collection.insert_one(entry)
    except Exception, e:
        pass

client.close()
