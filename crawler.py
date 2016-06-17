import urllib
import sqlite3
from html_parser import SuperPlacarParser

teams_db = sqlite3.connect("teams.db", check_same_thread=False)
teams_cur = teams_db.cursor()
teams_cur.execute('CREATE TABLE IF NOT EXISTS teams (user_id INTEGER PRIMARY KEY, name TEXT, last_score TEXT, last_score_board TEXT)')

def crawl():
	url = "http://www.superplacar.com.br/partidas-anteriores/2016-06-15"
	page = urllib.urlopen(url)
	content = page.read()

	parser = SuperPlacarParser(content)
	parser.parse_scores()

crawl()


