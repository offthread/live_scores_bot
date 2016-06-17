import urllib
import sqlite3
from html_parser import SuperPlacarParser


def crawl():
    url = "http://www.superplacar.com.br"
    page = urllib.urlopen(url)
    content = page.read()

    parser = SuperPlacarParser(content)
    parser.parse_scores()


crawl()
