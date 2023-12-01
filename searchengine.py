import json
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

# Improve the index by adding information (Done: Title)
# Improve the output by including title and teaser text (Done: title, TODO: Teaser Text)
# Install your search engine on the demo server provided 
#   vpn connection to university network
#   username: user029
#   password:WsP677k
#   ssh user029@vm520.rz.uni-osnabrueck.de
#   update app: touch searchengine.wsgi

# correct spelling mistakes, did you mean?
# sorting search hits

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
    results, results_len, query = perform_search(query)
    print('Amount Results: ', len(results))
    return render_template('results.html', query=query, results=results, results_len=results_len)

# handle all internal errors (500)
import traceback
@app.errorhandler(500)
def internal_error(exception):
   return "<pre>"+traceback.format_exc()+"</pre>"



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
        response = requests.get(current_url, timeout=0.5) # get requests
        status = response.status_code
        if status != 200: # status code 200 means everything went well
            continue
        soup = BeautifulSoup(response._content, 'html.parser') #print(soup.title.text) #print(soup.text) # text of entire page without html tags
        current_title = soup.title.text

        #print ('Title: ', current_title)
        #print ('Path: ', current_url)
        #print ('Content: ', soup.text)
        
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
    '''
    Performs search by querystring.
    '''
    print('starts searching')

    global ix

    with ix.searcher() as searcher:
        result_list = {"title": [], "path": []}

        parser = QueryParser("content", ix.schema)
        myquery = parser.parse(querystring)
        results = searcher.search(myquery)

        print('Number Results: ', len(results))
 
        # try to correct, if no results from querystring
        if len(results) == 0:
            corrected = searcher.correct_query(myquery, querystring)
            if corrected.query != myquery:
                print("CORRECT: ", corrected.string)
                querystring = corrected.string
                myquery = parser.parse(querystring)
                results = searcher.search(myquery)

        if len(results) > 0:
            for hit in results:
                fields = hit.fields()
                result_list['title'].append(fields['title'])
                result_list['path'].append(fields['path'])
        else:
            print('No Correction could be found for query string.')

        return result_list, len(result_list['title']), querystring