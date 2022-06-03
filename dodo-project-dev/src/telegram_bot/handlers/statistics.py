import asyncio
import itertools
from typing import Union

from aiogram.dispatcher.filters import Text, Command
from aiogram.types import Message, CallbackQuery, Update

import db
from db import redis_db
from telegram_bot import responses, filters
from telegram_bot.bot import dp
from telegram_bot.services import cache
from telegram_bot.services.api import get_revenue_statistics, get_being_late_certificates
from telegram_bot.utils.exceptions import DodoPublicAPIError
from utils import logger


@dp.errors_handler(exception=DodoPublicAPIError)
async def on_dodo_public_api_error(update: Update, exception):
    message = update.message or update.callback_query.message
    await message.answer('Произошла ошибка. Попробуйте ещё раз 😕')
    return True


@dp.message_handler(Command('reports'), state='*')
@dp.message_handler(Text('📊 Отчёты/Статистика'), state='*')
async def on_statistics_reports_list_command(query: Union[Message, CallbackQuery]):
    return responses.StatisticsReportsListResponse()


@dp.message_handler(
    Command('being_late_certificates'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
@dp.callback_query_handler(
    Text('being-late-certificates'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
async def on_being_late_certificates_command(query: Union[Message, CallbackQuery], departments):
    logger.info(f'User {query.from_user.id} is using being late certificates report')
    account_names = {department.account_name for department in departments}
    tasks = []
    for account_name in account_names:
        department_ids = [department.id for department in departments
                          if department.account_name == account_name]
        cookies = redis_db.get_cookies(account_name)
        tasks.append(get_being_late_certificates(cookies, department_ids))
    all_certificates = await asyncio.gather(*tasks)
    all_today_certificates = []
    all_week_before_certificates = []
    for today_certificates, week_before_certificates in all_certificates:
        all_today_certificates += today_certificates
        all_week_before_certificates += week_before_certificates
    return responses.BeingLateCertificatesResponse(all_today_certificates, all_week_before_certificates, departments)


@dp.message_handler(
    Command('delivery_speed'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
@dp.callback_query_handler(
    Text('delivery-speed'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
async def on_delivery_speed_command(query: Union[Message, CallbackQuery], departments):
    logger.info(f'User {query.from_user.id} is using delivery speed report')
    reports = db.DetailedDeliveryStatistics.select().join(db.Department).where(
        db.DetailedDeliveryStatistics.department.in_(departments))
    return responses.DeliverySpeedStatisticsResponse(reports)


@dp.message_handler(
    Command('bonus_system'),
    filters.ForwardingReportsInChatFilter(),
    state='*'
)
@dp.callback_query_handler(
    Text('bonus-system'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
async def on_bonus_system_command(query: Union[Message, CallbackQuery], departments):
    reports = db.OrdersStatistics.select().join(db.Department).where(
        db.OrdersStatistics.department.in_(departments))
    return responses.BonusSystemStatisticsResponse(reports)


@dp.message_handler(
    Command('delivery_awaiting_time'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
@dp.callback_query_handler(
    Text('delivery-awaiting-time'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
async def on_delivery_awaiting_time_command(query: Union[Message, CallbackQuery],
                                            departments):
    logger.info(f'User {query.from_user.id} is using delivery awaiting time report')
    reports = db.DeliveryStatistics.select().join(db.Department).where(
        db.DeliveryStatistics.department.in_(departments))
    return responses.DeliveryAwaitingTimeStatisticsResponse(reports)


@dp.message_handler(
    Command('delivery_performance'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
@dp.callback_query_handler(
    Text('delivery-performance'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
async def on_delivery_performance_command(query: Union[Message, CallbackQuery], departments):
    logger.info(f'User {query.from_user.id} is using delibery performance report')
    reports = db.DeliveryStatistics.select().join(db.Department).where(
        db.DeliveryStatistics.department.in_(departments))
    return responses.DeliveryPerformanceStatisticsResponse(reports)


@dp.message_handler(
    Command('awaiting_orders'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
@dp.callback_query_handler(
    Text('awaiting-orders'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
async def on_awaiting_orders_command(query: Union[Message, CallbackQuery], departments):
    logger.info(f'User {query.from_user.id} is using awaiting orders report')
    reports = db.DeliveryStatistics.select().join(db.Department).where(
        db.DeliveryStatistics.department.in_(departments))
    return responses.AwaitingOrdersStatisticsResponse(reports)


@dp.message_handler(
    Command('cooking_time'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
@dp.callback_query_handler(
    Text('cooking-time'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
async def on_cooking_time_command(query: Union[Message, CallbackQuery], departments):
    logger.info(f'User {query.from_user.id} is using cooking time report')
    reports = db.KitchenStatistics.select().join(db.Department).where(
        db.KitchenStatistics.department.in_(departments))
    return responses.CookingTimeStatisticsResponse(reports)


@dp.message_handler(
    Command('kitchen_performance'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
@dp.callback_query_handler(
    Text('kitchen-performance'),
    filters.ForwardingReportsInChatFilter(),
    state='*'
)
async def on_kitchen_performance_command(query: Union[Message, CallbackQuery], departments):
    logger.info(f'User {query.from_user.id} is using kitchen performance report')
    reports = db.KitchenStatistics.select().join(db.Department).where(
        db.KitchenStatistics.department.in_(departments))
    return responses.KitchenPerformanceStatisticsResponse(reports)


@dp.message_handler(
    Command('daily_revenue'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
@dp.callback_query_handler(
    Text('daily-revenue'),
    filters.ForwardingReportsInChatFilter(),
    state='*',
)
async def on_daily_revenue_command(query: Union[Message, CallbackQuery], departments):
    department_ids = [department.id for department in departments]
    cached_revenues_result = cache.get_daily_revenue_from_cache(department_ids)
    all_revenues = cached_revenues_result.cached_revenues
    if cached_revenues_result.missing_in_cache_department_ids:
        all_revenues += await get_revenue_statistics(
            cached_revenues_result.missing_in_cache_department_ids)
    cache.cache_daily_revenue_in_redis(all_revenues)
    return responses.DailyRevenueStatisticsResponse(all_revenues, departments)


@dp.message_handler(Command('daily_revenue'), state='*')
@dp.callback_query_handler(Text('daily-revenue'), state='*')
@dp.message_handler(Command('kitchen_performance'), state='*')
@dp.callback_query_handler(Text('kitchen-performance'), state='*')
@dp.message_handler(Command('cooking_time'), state='*')
@dp.callback_query_handler(Text('cooking-time'), state='*')
@dp.message_handler(Command('being_late_certificates'), state='*')
@dp.callback_query_handler(Text('being-late-certificates'), state='*')
@dp.message_handler(Command('delivery_speed'), state='*')
@dp.callback_query_handler(Text('delivery-speed'), state='*')
@dp.message_handler(Command('delivery_awaiting_time'), state='*')
@dp.callback_query_handler(Text('delivery-awaiting-time'), state='*')
@dp.message_handler(Command('delivery_performance'), state='*')
@dp.callback_query_handler(Text('delivery-performance'), state='*')
@dp.message_handler(Command('awaiting_orders'), state='*')
@dp.callback_query_handler(Text('awaiting-orders'), state='*')
async def on_no_reports_case(query: Union[Message, CallbackQuery]):
    return responses.StatisticsReportsNotConfiguredResponse()
