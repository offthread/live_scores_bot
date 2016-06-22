#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import sqlite3
import datetime


# create a subclass and override the handler methods
class SuperPlacarParser():
    def __init__(self, content):
        self.soup = BeautifulSoup(content, 'html.parser')
        self.create_schema()

    def create_schema(self):
        self.games_db = sqlite3.connect("live_scores.db", check_same_thread=False)
        self.games_cur = self.games_db.cursor()
        self.games_cur.execute(
            'CREATE TABLE IF NOT EXISTS game (match_day DATE, home_team_name TEXT, away_team_name TEXT, '
            'score TEXT, score_board_home TEXT, score_board_away TEXT, score_board_times_home TEXT, score_board_times_away TEXT, '
            'notify BOOLEAN, PRIMARY KEY (match_day, home_team_name, away_team_name))')
        self.games_db.commit()

        #for row in self.games_cur.execute('SELECT * FROM game'):
        #    print row

    def parse_scores(self):
        counter = 0
        for game in self.soup.find_all("div", {"class": "col-xs-12 item-wrapper"}):
            try:
                scorers_home = []
                scorers_home_time = []

                scorers_tags = self.soup.find_all("div", {"class": "goal-scores"})[counter]
                scorer_parser = BeautifulSoup("<html> " + scorers_tags.encode('latin-1').strip() + " </html>", 'html.parser')

                for scorer in scorer_parser.find_all("span", {"class": "goal-player"}):
                    scorers_home.append(scorer.contents[0].strip())

                for goal_time in scorer_parser.find_all("span", {"class": "goal-time"}):
                    scorers_home_time.append(goal_time.contents[0].strip())

                scorers_away = []
                scorers_away_time = []

                scorers_tags = self.soup.find_all("div", {"class": "goal-scores"})[counter + 1]
                scorer_parser = BeautifulSoup("<html> " + scorers_tags.encode('latin-1').strip() + " </html>", 'html.parser')

                for scorer in scorer_parser.find_all("span", {"class": "goal-player"}):
                    scorers_away.append(scorer.contents[0].strip())

                for goal_time in scorer_parser.find_all("span", {"class": "goal-time"}):
                    scorers_away_time.append(goal_time.contents[0].strip())

                team_home = \
                self.soup.find_all("div", {"class": "team-name"})[counter].children.next().children.next().contents[
                    0].strip()
                team_away = \
                self.soup.find_all("div", {"class": "team-name"})[counter + 1].children.next().children.next().contents[
                    0].strip()

                score_home = int(
                    self.soup.find_all("div", {"class": "team-score"})[counter].contents[0].encode('utf-8')) if len(
                    self.soup.find_all("div", {"class": "team-score"})[counter].contents) > 0 else None
                score_away = int(
                    self.soup.find_all("div", {"class": "team-score"})[counter + 1].contents[0].encode('utf-8')) if len(
                    self.soup.find_all("div", {"class": "team-score"})[counter + 1].contents) > 0 else None


                if score_home != None and score_away != None:
                    self.insert_or_update_game_in_database(team_home, team_away, score_home, score_away, scorers_home,
                                                           scorers_away, scorers_home_time, scorers_away_time)

            except Exception, e:
                print 'er:', e.message
                continue
            finally:
                counter += 2

    def insert_or_update_game_in_database(self, team_home, team_away, score_home, score_away, scorers_home,
                                          scorers_away, scorers_home_time, scorers_away_time):
        dt = datetime.datetime.now()
        if dt.hour ==  0:
            dt = dt - datetime.timedelta(hours=1)

        today = datetime.date(dt.year, dt.month, dt.day)

        # If the game still doesn't exist on database, add it to the records
        try:
            self.games_cur.execute("INSERT INTO game VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            today, team_home, team_away, str(score_home) + "x" + str(score_away), ",".join(scorers_home),
            ",".join(scorers_away), ",".join(scorers_home_time), ",".join(scorers_away_time), True))
            self.games_db.commit()

        # Otherwise, check is the scoreboard changed and update game highlights
        except:
            self.games_cur.execute('SELECT * FROM game WHERE match_day=? AND home_team_name=? AND away_team_name=?',
                                   (today, team_home, team_away))
            current_game = self.games_cur.fetchone()

            if current_game[3] != "%ix%i" % (score_home, score_away) and \
                    self.scorers_are_updated(score_home, score_away, scorers_home, scorers_away):
                self.games_cur.execute(
                    "UPDATE game SET score=?, score_board_home=?, score_board_away=?, score_board_times_home=?, score_board_times_away=?, notify=? WHERE match_day=? AND home_team_name=? AND away_team_name=?",
                    ("%ix%i" % (score_home, score_away), ",".join(scorers_home), ",".join(scorers_away),
                     ",".join(scorers_home_time), ",".join(scorers_away_time), True, today, team_home, team_away))
                self.games_db.commit()

    def scorers_are_updated(self, score_home, score_away, scorers_home, scorers_away):
        return len(scorers_home) == score_home and len(scorers_away) == score_away
