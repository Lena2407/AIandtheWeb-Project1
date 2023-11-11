import requests
from bs4 import BeautifulSoup
import re

TESTURL = 'https://vm009.rz.uos.de/crawl/index.html'
UNIURL = 'https://www.uos.de'

def crawl(start_url):
    '''
    Crawls (gets and parses) all the HTML pages on a certain server
    '''

    urls = [start_url]
    visited_urls = []

    split_url = start_url.split('/')
    server = split_url[2]
    base_url = split_url[0] + '//' + server

    while len(urls) != 0:
        current_url = urls.pop(0)
        visited_urls.append(current_url)

        # crawl for new url links
        r = requests.get(current_url, timeout=1)  #print(r.status_code) #print(r.headers)
        soup = BeautifulSoup(r._content, 'html.parser') #print(soup.title.text) #print(soup.text) # text of entire page without html tags
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

    #return urls
    
    

def main():

    index = {}
    
    crawl(TESTURL)
    #print(urls)
    #crawl(UNIURL)


if __name__ == "__main__":
    main()
