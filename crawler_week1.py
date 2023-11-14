import requests
from bs4 import BeautifulSoup
import re

TESTURL = 'https://vm009.rz.uos.de/crawl/index.html'
UNIURL = 'https://www.uos.de'

# week 2: flask app and index with whoosh library
# flask app: 2 urls, 
#   get home url (show search form)
#   get search url with parameter q: 
#       Search for q using the index and display a 
#       list of URLs as links

global index

def crawl(start_url):
    '''
    Crawls (gets and parses) all the HTML pages on a certain server
    '''
    global index

    urls = [start_url]
    visited_urls = []
    index = {}

    split_url = start_url.split('/')
    server = split_url[2]
    base_url = split_url[0] + '//' + server

    while len(urls) != 0:
        current_url = urls.pop(0)
        visited_urls.append(current_url)

        # crawl for new url links
        response = requests.get(current_url, timeout=0.1) # get requests
        status = response.status_code
        if status != 200: # status code 200 means everything went well
            continue
        soup = BeautifulSoup(response._content, 'html.parser') #print(soup.title.text) #print(soup.text) # text of entire page without html tags
       
        update_index(index, current_url, soup.text)

        
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

    index = dict( sorted(index.items(), key=lambda x: x[0].lower()) )


    for k,v in index.items():
        print('{}:{}'.format(k,v))


    #return urls
    
def update_index(index, url, text):
    print('index_update')
    words = list(set(re.sub(r'[^\w\s]','',text).split())) # remove doubled entries
    #print(words)

    for word in words:
        if word in index.keys():
            index[word].append(url)
        else:
            index[word] = [url]

    index = dict( sorted(index.items(), key=lambda x: x[0].lower()) ) # sort list




def search(keys):
    print('SEARCH')
    global index
    urls = [] # urls that contain all keywords

    possible_urls = [] # candidates

    for key in keys:
        possible_urls.extend(index[key])
    possible_urls = list(set(possible_urls))
    urls = possible_urls

    print('Possible URLS: ', possible_urls)

    removing_urls = []
    for key in keys:
        print('Key: ', key)
        print('Right URLS: ', index[key])
        for url in possible_urls:
            print('checking url: ', url,' for key ', key)
            if url not in index[key]:
                print('not in key ', key, ' is: ', url)
                removing_urls.append(url)
    for url in removing_urls:
        urls.remove(url)
    

    return urls


def main():
    
    crawl(TESTURL)

    keywords = ['that', 'That'] # casefold? ignore upper or lower case letters!!
    results = search(keywords)
    print('RESULTS: ', results)




if __name__ == "__main__":
    main()
