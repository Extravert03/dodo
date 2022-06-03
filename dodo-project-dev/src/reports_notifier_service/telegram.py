import contextlib
import time

from aiogram import executor, Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.utils.exceptions import TelegramAPIError

import config

bot = Bot(config.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)


def send_message(chat_id: int, text: str):
    for _ in range(3):
        with contextlib.suppress(TelegramAPIError):
            executor.start(dp, bot.send_message(chat_id, text))
            time.sleep(0.1)
            break
