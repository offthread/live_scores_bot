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

## License ##
This software is licensed under the Apache 2 license, quoted below.

Copyright 2016 OFF Thread <offthread@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.

## Contributing ##

Feel free to contribute using your own bot.
