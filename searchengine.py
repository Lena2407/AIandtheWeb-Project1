'''
Simple Search Engine

A simple search engine that performs a search for entered search queries 
on a beforehand established index of the whoosh library. The search engine
can be used with the help of a flask app. To use the search engine the 
following link can be opend. Be aware, that a connection to the wifi of 
University of Osnabrueck has to be established.

http://vm520.rz.uni-osnabrueck.de/user029/searchengine.wsgi

authors: Lena Brueggemann, Dalva Pauline Beeck
'''

from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh import index
from flask import Flask, request, render_template, redirect, url_for

TESTURL = 'https://vm009.rz.uos.de/crawl/index.html'
UNIURL = 'https://www.uos.de'

app = Flask(__name__)

# Home route ('/')
@app.route('/', methods=['GET', 'POST'])
def home():
    '''
    Renders the 'index.html' template and redirects to the search route 
    when a search query is entered.
    '''
    if request.method == 'POST':
        query = request.form.get('query', '')
        # Redirect to the search route with the user's query
        return redirect(url_for('search', query=query))
    # If it's a GET request, render the home template ('index.html')
    return render_template('index.html')

# Search route ('/search')
@app.route('/search')
def search():
    '''
    Gets the user's query from the URL parameters, perform the search operation 
    and gets results, renders the 'results' template.
    '''
    query = request.args.get('query', '')
    results, results_len, real_query, correction = perform_search(query)
    return render_template('results.html', real_query=real_query, results=results, results_len=results_len, correction=correction, old_query=query)

# handle all internal errors (500)
import traceback
@app.errorhandler(500)
def internal_error(exception):
   return "<pre>"+traceback.format_exc()+"</pre>"

def perform_search(querystring):
    '''
    Performs a search for the querystring using the indexdir.

    Attributes:
        querystring: A string of words to search for in the content of the index.
    
    Returns:
        sorted_dict: A dictionary that contains the results with the keys title, path and a teaser text.
        len(sorted_dict['title']): An integer that specifies the amount of results found.
        querystring: A string that was used as the search query for the performed search.
        correction: A boolean that indicates, if the search query was corrected (True) or not (False).
    '''
    # use the stored index to perform the search
    ix = index.open_dir("indexdir")

    with ix.searcher() as searcher:
        result_list = {"title": [], "path": [], "teaser": []}
        sorted_dict = {"title": [], "path": [], "teaser": []}
        correction = False

        # perform the search with the given querystring
        parser = QueryParser("content", ix.schema)
        myquery = parser.parse(querystring)
        results = searcher.search(myquery)
 
        # try once to correct search query, if no results from querystring were found
        if len(results) == 0:
            corrected = searcher.correct_query(myquery, querystring)
            if corrected.query != myquery:
                correction = True
                # perform the search again, if query could be corrected
                querystring = corrected.string
                myquery = parser.parse(querystring)
                results = searcher.search(myquery)

        # store and sort search results, if any were found
        if len(results) > 0:
            for hit in results:
                fields = hit.fields()
                result_list['title'].append(fields['title'])
                result_list['path'].append(fields['path'])
                result_list['teaser'].append(fields['teaser'])

            # sorting search hits alphabetically
            combined_pairs = zip(result_list['title'], result_list['path'], result_list['teaser'])
            sorted_pairs = sorted(combined_pairs, key=lambda x: x[0])
            sorted_first_key, sorted_second_key, sorted_third_key = zip(*sorted_pairs)

            # Create a new dictionary with the sorted lists
            sorted_dict = {'title': list(sorted_first_key), 'path': list(sorted_second_key), 'teaser': list(sorted_third_key)}

        return sorted_dict, len(sorted_dict['title']), querystring, correction