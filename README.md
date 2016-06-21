# live_scores_bot
A Telegram bot that notifies people about the live scores of their preferred soccer teams (only brazilian teams, currently). Brazilian scores are powered by http://www.superplacar.com.br/

If you are a Telegram user, you can include this bot (@live_scores_bot) into a channel or write commands directly on a private chat.

We support the following commands:

* /addteam <team> - To start monitoring the scores of a team

* /removeteam - To stop monitoring the scores of a team

* /listtteams - To check which teams you're currently monitoring

## Example of usage ##
* /addteam Flamengo         -> To start monitoring Flamengo's scores
* /removeteam Flamengo      -> To stop monitoring Flamengo's scores

## Project Configuration ##

This project is configured to run using the following configuration:

* Python version - 2.7.6
* Telepot version - 7.1
* BeautifulSoup - 4.4.1

## Deployment Instructions ##

```python
python crawler
```
to start crawling the http://superplacar.com.br webpage

```python
python bot <YOUR_BOT_TOKEN>
```
to start the bot
