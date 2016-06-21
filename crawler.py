import urllib2
import time
import sqlite3
from html_parser import SuperPlacarParser

def crawl():
    try:
        url = "http://www.superplacar.com.br"
        opener = urllib2.build_opener()
        opener.addheaders = [('Accept-Charset', 'utf-8')]
        url_response = opener.open(url)
        content = url_response.read().decode('utf-8')

        parser = SuperPlacarParser(content)
        parser.parse_scores()

    except:
         print "error"
         time.sleep(30)
         crawl()

while True:
    print "Crawling..."
    crawl()
    time.sleep(30)
