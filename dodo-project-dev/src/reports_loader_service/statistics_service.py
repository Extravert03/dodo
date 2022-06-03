import asyncio
from datetime import datetime, timedelta
from typing import Iterable

import db
from db import redis_db
from dodo_api import (
    DeliveryStatistics,
    KitchenStatistics,
    DetailedDeliveryStatistics,
)
from dodo_api.services import get_restaurant_orders
from dodo_api.utils import time_utils
from utils import logger


async def get_detailed_delivery_statistics(cookies: dict, department_ids: Iterable[int]):
    today_date = time_utils.get_now_datetime().format('DD.MM.YYYY')
    return await DetailedDeliveryStatistics(cookies, department_ids, today_date, today_date).get_data()


async def get_delivery_statistics(cookies: dict, department_id: int):
    return await DeliveryStatistics(cookies, department_id).get_data()


async def get_kitchen_statistics(cookies: dict, department_id: int):
    return await KitchenStatistics(cookies, department_id).get_data()


async def update_kitchen_statistics():
    logger.debug('kitchen statistics updating')
    departments = db.Department.select()
    for department in departments:
        cookies = redis_db.get_cookies(department.account_name)
        new_statistics = await get_kitchen_statistics(cookies, department.id)
        kitchen_statistics: db.KitchenStatistics = db.KitchenStatistics.get(department=department)
        kitchen_statistics.average_cooking_time = new_statistics.average_cooking_time.in_seconds()
        kitchen_statistics.revenue_per_hour = new_statistics.revenue_per_hour
        kitchen_statistics.revenue_increase_over_week_ago = new_statistics.revenue_increase_over_week_ago
        kitchen_statistics.products_spending_per_hour = new_statistics.products_spending_per_hour
        kitchen_statistics.products_spending_increase_over_week_ago = new_statistics.products_spending_increase_over_week_ago
        kitchen_statistics.postponed = new_statistics.postponed
        kitchen_statistics.in_queue = new_statistics.in_queue
        kitchen_statistics.in_work = new_statistics.in_work
        kitchen_statistics.updated_at = datetime.now(time_utils.MOSCOW_UTC)
        kitchen_statistics.save()


async def update_delivery_statistics():
    logger.debug('delivery statistics updating')
    departments = db.Department.select()
    for department in departments:
        cookies = redis_db.get_cookies(department.account_name)
        new_statistics = await get_delivery_statistics(cookies, department.id)
        delivery_statistics: db.DeliveryStatistics = db.DeliveryStatistics.get(department=department)
        delivery_statistics.increase_over_week_ago = new_statistics.increase_over_week_ago
        delivery_statistics.deliveries_amount_per_hour = new_statistics.deliveries_amount_per_hour
        delivery_statistics.awaiting_orders_amount = new_statistics.awaiting_orders_amount
        delivery_statistics.couriers_total_amount = new_statistics.couriers_total_amount
        delivery_statistics.couriers_in_queue_amount = new_statistics.couriers_in_queue_amount
        delivery_statistics.delivery_awaiting_time = new_statistics.delivery_awaiting_time.in_seconds()
        delivery_statistics.updated_at = datetime.now(time_utils.MOSCOW_UTC)
        delivery_statistics.save()


async def update_orders_statistics():
    departments = db.Department.select()
    account_names = {department.account_name for department in departments}
    date = datetime.utcnow().strftime('%d.%m.%Y')
    for account_name in account_names:
        department_ids = {department.id for department in departments if department.account_name == account_name}
        department_ids = list(department_ids)
        cookies = redis_db.get_cookies(account_name)
        orders = await get_restaurant_orders(cookies, department_ids, date)
        for department in departments:
            orders_by_department = [order for order in orders if order.department.lower().strip() == department.name.lower()]
            if not orders_by_department:
                continue
            orders_statistics = db.OrdersStatistics.get(department=department)
            orders_statistics.customers_with_bonus = len([order for order in orders_by_department if order.customer_phone_number])
            orders_statistics.total_customers = len(orders_by_department)
            orders_statistics.save()


async def update_detailed_delivery_statistics():
    logger.debug('detailed delivery statistics updating')
    departments = db.Department.select()
    account_names = {department.account_name for department in departments}
    for account_name in account_names:
        department_ids = {department.id for department in departments if department.account_name == account_name}
        cookies = redis_db.get_cookies(account_name)
        new_statistics = await get_detailed_delivery_statistics(cookies, department_ids)
        for statistics in new_statistics:
            department = [department for department in departments if department.name == statistics.department][0]
            (db.DetailedDeliveryStatistics.update(
                total_average_time=statistics.total_average_time.in_seconds(),
                average_cooking_time=statistics.average_cooking_time.in_seconds(),
                average_awaiting_on_heat_shelf_time=statistics.average_awaiting_on_heat_shelf_time.in_seconds(),
                average_delivery_time=statistics.average_delivery_time.in_seconds(),
                updated_at=datetime.now(time_utils.MOSCOW_UTC),
            ).where(db.DetailedDeliveryStatistics.department == department).execute())
