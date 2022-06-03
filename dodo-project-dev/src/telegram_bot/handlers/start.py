from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message

from telegram_bot.bot import dp
from telegram_bot import responses


@dp.message_handler(CommandStart(), state='*')
async def on_start_command(message: Message):
    return responses.MainMenuResponse()
