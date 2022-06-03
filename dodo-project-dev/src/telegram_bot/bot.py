from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, ParseMode

import config
from telegram_bot.middlewares import ProcessResponseMiddleware

__all__ = (
    'bot',
    'dp',
    'on_startup',
)

bot = Bot(token=config.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)

dp = Dispatcher(bot, storage=MemoryStorage())


async def setup_commands(dispatcher: Dispatcher):
    pass
    await dispatcher.bot.set_my_commands([
        BotCommand('start', '👨‍💻 Главное меню'),
        BotCommand('settings', '⚙️ Настройки'),
        BotCommand('reports', '🔎 Отчёты по статистике'),
        BotCommand('bonus_system', 'Бонусная система'),
        BotCommand('cooking_time', 'Время приготовления'),
        BotCommand('daily_revenue', 'Выручка за сегодня'),
        BotCommand('delivery_speed', 'Скорость доставки'),
        BotCommand('delivery_awaiting_time', 'Время на полке'),
        BotCommand('kitchen_performance', 'Производительность кухни'),
        BotCommand('delivery_performance', 'Производительность доставки'),
        BotCommand('being_late_certificates', 'Сертификаты за опоздание'),
        BotCommand('awaiting_orders', 'Заказов остывает на полке - курьеры всего / в очереди'),
    ])


async def on_startup(dispatcher: Dispatcher):
    dispatcher.setup_middleware(ProcessResponseMiddleware(dispatcher.bot))
    await setup_commands(dispatcher)
