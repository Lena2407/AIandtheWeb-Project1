'''
Simple Crawler

A simple crawler that creates an index for a given start url and all
its url references that lead to the ssame server. The index is build 
using the whoosh library.

authors: Lena Brueggemann, Dalva Pauline Beeck
'''

import os
import requests
from bs4 import BeautifulSoup
import re

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.query import *

TESTURL = 'https://vm009.rz.uos.de/crawl/index.html'

def crawl(start_url):
    '''
    Crawls (gets and parses) all the HTML pages on a certain server. 
    Builds an index with the whoosh library, which can be later used 
    to perform searches on the content of the HTML pages.

    Attributes:
        start_url = a string that is a url, which shall be used to start the search.
    '''
    # the index stores the title, pat, content and a teaser text
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT, teaser=TEXT(stored=True))
    if not os.path.exists("index"):
        os.mkdir("index")
    ix = create_in("index", schema)
    # the writer is used to add entries into the index
    writer = ix.writer()
    # list of all the urls that shall be added to the index
    urls = [start_url]
    # list of all visited urls, to prevent doubled enties
    visited_urls = []

    split_url = start_url.split('/')
    server = split_url[2] # server to search on
    base_url = split_url[0] + '//' + server # url to server

    url_without_html = '' # url without the HTML page at the end
    split_url.pop()
    for part in split_url:
        url_without_html += part + '/'

    # there are still urls to be added to the index
    while len(urls) != 0:
        current_url = urls.pop(0)
        visited_urls.append(current_url)

        # crawl for new url links
        response = requests.get(current_url, timeout=3)
        status = response.status_code
        if status != 200: # status code 200 means everything went well
            continue
        # get html content with beautifulsoup4
        soup = BeautifulSoup(response._content, 'html.parser') 
        current_title = soup.title.text # title
        teaser = soup.find('p').text # teaser
        if len(teaser) > 100:
            teaser = (teaser[:100] + '..')

        # add currnet url to index
        writer.add_document(title=current_title, path=current_url, content=soup.text, teaser=teaser)
        
        # find links (urls) in content by searching for <a href="...">Text</a>
        for link in soup.find_all('a'):
            url = link['href']

            # full url: check if same server with base_url
            if 'http' in url:
                if base_url in url:
                    if url not in visited_urls:
                        urls.append(url)
            # subpage of url starting with '/': add base_url to create working url
            elif url[0] == '/':
                url = base_url + url
                if url not in visited_urls:
                    urls.append(url)
            # HTML page: exchange HTML pages
            elif re.search(r'^[a-z0-9]+\.html$', url): 
                url = url_without_html + url
                if url not in visited_urls:
                    urls.append(url)
            # none of the above: can not be handled
            else:
                print('did not understand url: ', url)

    # commit entries to index
    writer.commit()

def main():
    crawl(TESTURL)

if __name__ == "__main__":
    main()
