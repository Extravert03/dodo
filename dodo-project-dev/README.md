# Dodo Bot

## Installation

- Install dependencies.
- Create `accounts.json` with accounts in this format:
```
{
    "bot_token": "bot token",
    "name": "unique account name, must starts with 'shift' or 'office'",
    "login": "login in IS",
    "password": "password in IS"
}
```
- Run [Telegram Notifier](https://github.com/usbtypec1/tg-notifier).
- Setup .env file (see .env.dist example)
- Run `run_services.py` and `run_telegram_bot.py` scripts.