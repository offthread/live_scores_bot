from bs4 import BeautifulSoup

# create a subclass and override the handler methods
class SuperPlacarParser():
	def __init__(self, content):
		self.soup = BeautifulSoup(content, 'html.parser')

	def parse_scores(self):
		counter = 0
		for game in self.soup.find_all("div", { "class" : "col-xs-12 item-wrapper"} ):
			try:
				scorers_home = []
				scorers_home_time = []

				scorers_tags = self.soup.find_all("div", { "class" : "goal-scores"} )[counter]
				scorer_parser = BeautifulSoup("<html> " + str(scorers_tags) + " </html>", 'html.parser')

				for scorer in scorer_parser.find_all("span", { "class" : "goal-player"} ):
					scorers_home.append(scorer.contents[0])

				for goal_time in scorer_parser.find_all("span", { "class" : "goal-time"} ):
					scorers_home_time.append(goal_time.contents[0])

				scorers_away = []
				scorers_away_time = []

				scorers_tags = self.soup.find_all("div", { "class" : "goal-scores"} )[counter+1]
				scorer_parser = BeautifulSoup("<html> " + str(scorers_tags) + " </html>", 'html.parser')

				for scorer in scorer_parser.find_all("span", { "class" : "goal-player"} ):
					scorers_away.append(scorer.contents[0])

				for goal_time in scorer_parser.find_all("span", { "class" : "goal-time"} ):
					scorers_away_time.append(goal_time.contents[0])


				team_home = self.soup.find_all("div", { "class" : "team-name"} )[counter].children.next().children.next().contents[0].strip()
				team_away = self.soup.find_all("div", { "class" : "team-name"} )[counter+1].children.next().children.next().contents[0].strip()
				score_home = int(self.soup.find_all("div", { "class" : "team-score"} )[counter].contents[0].encode('utf-8'))
				score_away = int(self.soup.find_all("div", { "class" : "team-score"} )[counter+1].contents[0].encode('utf-8'))
				print "Score: %s %ix%i %s" % (team_home, score_home, score_away, team_away)
				print "Scorers from home team: " + str(scorers_home)
				print "Goal times: " + str(scorers_home_time)
				print "Scorers from away team: " + str(scorers_away)
				print "Goal times: " + str(scorers_away_time)

				#TODO store values on database for further querying
				print 

			except:
				continue
			finally:
				counter+=2
			
			
		#print self.soup.find_all("div", { "class" : "team-score"} )[1]
