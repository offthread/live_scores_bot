#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telepot
import sqlite3
import threading
import time
import datetime
import sys

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if (content_type == 'text'):
        message_words = msg['text'].strip().lower().split()
        if (msg['text'][0] != "/"):
            return
        else:
            if (message_words[0].replace("/addteam@live_scores_bot", "/addteam") == "/addteam"):
                add_team(msg)
            elif (message_words[0].replace("/removeteam@live_scores_bot", "/removeteam") == "/removeteam"):
                remove_team(msg)
            elif (message_words[0].replace("/listteams@live_scores_bot", "/listteams") == "/listteams"):
                list_teams(msg)


def add_team(msg):
    requested_team = " ".join(msg["text"].split(" ")[1:len(msg["text"].split(" "))]).strip()

    if len(requested_team) == 0:
        bot.sendMessage(msg['chat']['id'],
                        "Please inform the team to be added to the watchlist. Your team name must follow the nomenclature"
                        " defined by http://www.superplacar.com.br",
                        reply_to_message_id=msg['message_id'])

    else:
        existing_entry = notifications_cur.execute("SELECT * FROM notification WHERE team = ?",
                                                   (requested_team,)).fetchall()
        if len(existing_entry) == 0:
            notifications_cur.execute('INSERT INTO notification VALUES (?, ?)', (requested_team, msg['chat']['id']))
            bot.sendMessage(msg['chat']['id'],
                            "Now monitoring team %s" % requested_team,
                            reply_to_message_id=msg['message_id'])
        else:
            if unicode(msg['chat']['id']) in existing_entry[0][1]:
                bot.sendMessage(msg['chat']['id'],
                                "You're already monitoring %s" % requested_team,
                                reply_to_message_id=msg['message_id'])
            else:
                notifications_cur.execute('UPDATE notification SET subscribed_users = ? WHERE team = ?',
                                          (existing_entry[0][1] + "," + str(msg['chat']['id']), requested_team))
                bot.sendMessage(msg['chat']['id'],
                                "Now monitoring team %s" % requested_team,
                                reply_to_message_id=msg['message_id'])

        notifications_db.commit()

def remove_team(msg):
    requested_team = " ".join(msg["text"].split(" ")[1:len(msg["text"].split(" "))])

    if len(requested_team) == 0:
        bot.sendMessage(msg['chat']['id'],
                        "Please inform the team to be removed from the watchlist",
                        reply_to_message_id=msg['message_id'])

    else:
        existing_entry = notifications_cur.execute("SELECT * FROM notification WHERE team = ?",
                                                   (requested_team,)).fetchall()
        if len(existing_entry) > 0:
            groups_monitoring_team = existing_entry[0][1].split(",")
            if not unicode(msg['chat']['id']) in groups_monitoring_team:
                bot.sendMessage(msg['chat']['id'],
                                "You're not currently monitoring %s" % requested_team,
                                reply_to_message_id=msg['message_id'])
            else:
                groups_monitoring_team.remove(unicode(msg['chat']['id']))
                if len(groups_monitoring_team) > 0:
                    subscribed_users = ",".join(groups_monitoring_team, )
                    notifications_cur.execute('UPDATE notification SET subscribed_users = ?',
                                          (subscribed_users,))
                else:
                    notifications_cur.execute('DELETE FROM notification WHERE team = ?',
                                                   (requested_team,))
                bot.sendMessage(msg['chat']['id'],
                                "You're not monitoring %s anymore" % requested_team,
                                reply_to_message_id=msg['message_id'])
            notifications_db.commit()
        else:
            bot.sendMessage(msg['chat']['id'],
                            "You're not currently monitoring %s" % requested_team,
                            reply_to_message_id=msg['message_id'])

def list_teams(msg):
    subscriptions = notifications_cur.execute('SELECT team FROM notification WHERE subscribed_users LIKE ? ',
                                              ("%" + str(msg['chat']['id']) + "%",)).fetchall()

    if len(subscriptions) == 0:
        bot.sendMessage(msg['chat']['id'],
                        "You're following no teams currently",
                        reply_to_message_id=msg['message_id'], parse_mode='HTML')

    else:
        message = ""
        for subscription in subscriptions:
            message+="- %s\n" % subscription[0]

        bot.sendMessage(msg['chat']['id'],
                        "You're currently monitoring the following teams:\n%s" % message,
                        reply_to_message_id=msg['message_id'], parse_mode='HTML')


def tgram_bot():
    bot.message_loop(handle)


def get_game_updates(day, home_team, away_team):
    game_updates = {"started": False, "goal_home": False,
                    "goal_away": False, "scorer": False, "time": False}

    game = notifications_cur.execute("SELECT * FROM game WHERE home_team_name=? AND away_team_name=? AND match_day=?",
                                     (home_team, away_team, day)).fetchall()[0]

    if game[3] == u"0x0":
        game_updates["started"] = True

    elif len(game[6]) > 0 and len(game[6].split(",")) > 0 and len(game[7]) > 0 and len(game[7].split(",")) > 0:
        home_team_last_goal = game[6].split(",")[-1]
        away_team_last_goal = game[7].split(",")[-1]

        if home_team_last_goal.split(" ")[1] == "2T" and away_team_last_goal.split(" ")[1] == "1T":
            game_updates["goal_home"] = True
            game_updates["time"] = home_team_last_goal
        elif home_team_last_goal.split(" ")[1] == "1T" and away_team_last_goal.split(" ")[1] == "2T":
            game_updates["goal_away"] = True
            game_updates["time"] = away_team_last_goal
        else:
            if int(home_team_last_goal.split(" ")[0].replace("'", "")) > int(
                    away_team_last_goal.split(" ")[0].replace("'", "")):
                game_updates["goal_home"] = True
                game_updates["time"] = home_team_last_goal
            else:
                game_updates["goal_away"] = True
                game_updates["time"] = away_team_last_goal
    else:
        home_team_last_goal = game[6].split(",")[-1]
        away_team_last_goal = game[7].split(",")[-1]
        if len(game[6]) == 0:
            game_updates["goal_away"] = True
            game_updates["time"] = away_team_last_goal
        else:
            game_updates["goal_home"] = True
            game_updates["time"] = home_team_last_goal

    if game_updates["goal_home"]:
        game_updates["scorer"] = game[4].split(",")[-1]
    elif game_updates["goal_away"]:
        game_updates["scorer"] = game[5].split(",")[-1]

    game_updates["scoreboard"] = game[3]
    return game_updates


def listenToUpdates():
    while True:
        print "Checking for updates"
        dt = datetime.datetime.now()
        today = datetime.date(dt.year, dt.month, dt.day)
        scores_to_notify = notifications_cur.execute("SELECT * FROM game WHERE notify = ? AND match_day = ?",
                                                     (1, today)).fetchall()

        for score in scores_to_notify:
            home_team = score[1]
            away_team = score[2]

            updates = get_game_updates(today, home_team, away_team)

            users_to_notify_for_home_team = notifications_cur.execute("SELECT * FROM notification WHERE team = ?",
                                                                      (home_team,)).fetchall()
            notified_users = []
            if len(users_to_notify_for_home_team) > 0:
                for user in users_to_notify_for_home_team[0][1].split(","):
                    notified_users.append(user)
                    if updates["started"]:
                        bot.sendMessage(user, "%s x %s has started. Scoreboard is 0x0!" % (home_team, away_team))

                    elif updates["goal_home"]:
                        bot.sendMessage(user, "Goal from %s! %s scores at %s. Scoreboard is now %s %s %s!" %
                                        (home_team, updates["scorer"], updates["time"], home_team, updates["scoreboard"],
                                         away_team))
                    else:
                        bot.sendMessage(user, "Goal from %s! %s scores at %s. Scoreboard is now %s %s %s!" %
                                        (away_team, updates["scorer"], updates["time"], home_team, updates["scoreboard"],
                                         away_team))

            users_to_notify_for_away_team = notifications_cur.execute("SELECT * FROM notification WHERE team = ?",
                                                                      (away_team,)).fetchall()

            if len(users_to_notify_for_away_team) > 0:
                for user in users_to_notify_for_away_team[0][1].split(","):
                    if user not in notified_users:
                        if updates["started"]:
                            bot.sendMessage(user, "%s x %s has started. Scoreboard is 0x0!" % (home_team, away_team))

                        elif updates["goal_away"]:
                            bot.sendMessage(user, "Goal from %s! %s scores at %s. Scoreboard is now %s %s %s!" %
                                            (away_team, updates["scorer"], updates["time"], home_team, updates["scoreboard"],
                                             away_team))

                        else:
                            bot.sendMessage(user, "Goal from %s! %s scores at %s. Scoreboard is now %s %s %s!" %
                                            (home_team, updates["scorer"], updates["time"], home_team, updates["scoreboard"],
                                             away_team))

            notifications_cur.execute("UPDATE game SET notify = ? WHERE home_team_name = ? AND away_team_name = ?"
                                      "AND match_day=?", (0, home_team, away_team, today))
            notifications_db.commit()

        time.sleep(30)

if len(sys.argv) > 1:
    notifications_db = sqlite3.connect("live_scores.db", check_same_thread=False)
    notifications_cur = notifications_db.cursor()

    notifications_cur.execute(
        'CREATE TABLE IF NOT EXISTS notification (team TEXT, subscribed_users TEXT )')

    notifications_db.commit()

    bot = telepot.Bot(sys.argv[1])

    t = threading.Thread(target=tgram_bot)
    t.daemon = True
    t.start()

    print("I have successfully spun off the telegram bot")

    listenToUpdates()

else:
    print "usage: bot.py bot_key\n" \
          "prog.py: error: the following arguments are required: bot_key"
