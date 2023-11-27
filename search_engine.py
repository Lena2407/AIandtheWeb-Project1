import os
import requests
from bs4 import BeautifulSoup
import re

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser

from flask import Flask, request, render_template, redirect, url_for



TESTURL = 'https://vm009.rz.uos.de/crawl/index.html'
UNIURL = 'https://www.uos.de'

# uikit example for frontend

# week 2: flask app 
# flask app: 2 urls, 
#   get home url (show search form)
#   get search url with parameter q: 
#       Search for q using the index and display a 
#       list of URLs as links

global ix

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query', '')
        # Redirect to the search route with the user's query
        return redirect(url_for('search', query=query))
    return render_template('index.html')

@app.route('/search')
def search():
    crawl(TESTURL)
    query = request.args.get('query', '')
    results = perform_search(query)
    print('Amount Results: ', len(results))
    return render_template('results.html', query=query, results=results)


def crawl(start_url):
    '''
    Crawls (gets and parses) all the HTML pages on a certain server
    '''
    global ix

    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    if not os.path.exists("index"):
        os.mkdir("index")
    ix = create_in("index", schema)

    writer = ix.writer()


    urls = [start_url]
    visited_urls = []

    split_url = start_url.split('/')
    server = split_url[2]
    base_url = split_url[0] + '//' + server

    while len(urls) != 0:
        current_url = urls.pop(0)
        visited_urls.append(current_url)

        # crawl for new url links
        response = requests.get(current_url, timeout=5) # get requests
        status = response.status_code
        if status != 200: # status code 200 means everything went well
            continue
        soup = BeautifulSoup(response._content, 'html.parser') #print(soup.title.text) #print(soup.text) # text of entire page without html tags
        current_title = soup.title.text

        print ('Title: ', current_title)
        print ('Path: ', current_url)
        print ('Content: ', soup.text)
        
        writer.add_document(title=current_title, path=current_url, content=soup.text)
        
        # find links (urls) in content
        # <a href="...">Text</a>
        for link in soup.find_all('a'):
            url = link['href']

            # Full link
            if 'http' in url:
                if base_url in url:
                    if url not in visited_urls:
                        urls.append(url)
            elif url[0] == '/':
                url = base_url + url
                if url not in visited_urls:
                    urls.append(url)
            # replace last part of path if no '/' as starting point
            elif re.search(r'^[a-z0-9]+\.html$', url): 
                #print('subpage: ', url)
                if 'index.html' in current_url:
                    current_url_main = current_url.split('index.html')[0]
                url = current_url_main + url
                #print('new: ', url)
                if url not in visited_urls:
                    urls.append(url)
                #print(link['href']) # extracting urls of website
                #print(link.text)

            else:
                print('did not understand url: ', url)

    print(visited_urls)
    writer.commit()


def perform_search(querystring):
    print('starts searching')

    global ix

    with ix.searcher() as searcher:
        parser = QueryParser("content", ix.schema)
        myquery = parser.parse(querystring)
        results = searcher.search(myquery)

        print('Number Results: ', len(results))
        if len(results) > 0:
            for result in results:
                print(result)
        return results
