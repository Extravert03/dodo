from aiogram import executor

import telegram_bot.handlers
from telegram_bot.bot import dp, on_startup

if __name__ == '__main__':
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
    )
