import asyncio

import db
from db import redis_db
from dodo_api import serializers
from dodo_api.services import PizzeriaStopSales, IngredientStopSales, SectorStopSales, StreetStopSales
from dodo_api.utils import time_utils
from utils import logger


async def run_pizzeria_stop_sales():
    departments = db.Department.select()
    account_names = {department.account_name for department in departments}
    today = time_utils.get_today_date().format('DD.MM.YYYY')
    for account_name in account_names:
        department_ids = tuple({department.id for department in departments if
                                department.account_name == account_name})
        cookies = redis_db.get_cookies(account_name)
        stop_sales = await PizzeriaStopSales(cookies, department_ids, today, today).get_data()
        for stop_sale in stop_sales:
            if stop_sale.renewer_name is not None:
                continue
            logger.debug(f'new pizzeria stop sale {stop_sale.department}')
            serializer = serializers.PizzeriaStopSaleSerializer(stop_sale)
            redis_db.add_report_notification_to_queue(serializer.as_json())


def is_valid_ingredient(ingredient: str):
    valid_ingredients = (('моцарелла',), ('сыр', 'моцарелла'), ('пицца', 'соус',),
                         ('пицца-соус',), ('тесто',))
    for valid_ingredients_pair in valid_ingredients:
        if all((valid_ingredient in ingredient) for valid_ingredient in valid_ingredients_pair):
            return True
    return False


async def run_ingredient_stop_sales():
    departments = db.Department.select()
    account_names = {department.account_name for department in departments}
    today = time_utils.get_today_date().format('DD.MM.YYYY')
    for account_name in account_names:
        department_ids = tuple({department.id for department in departments if
                                department.account_name == account_name})
        cookies = redis_db.get_cookies(account_name)
        stop_sales = await IngredientStopSales(cookies, department_ids, today, today).get_data()
        for stop_sale in stop_sales:
            if stop_sale.renewer_name is not None:
                continue
            if not is_valid_ingredient(stop_sale.ingredient.lower()):
                continue
            logger.debug(f'new ingredient stop sale {stop_sale.department} {stop_sale.ingredient}')
            serializer = serializers.IngredientsStopSaleSerializer(stop_sale)
            redis_db.add_report_notification_to_queue(serializer.as_json())


async def run_sector_stop_sales():
    departments = db.Department.select()
    account_names = {department.account_name for department in departments}
    today = time_utils.get_now_datetime().format('DD.MM.YYYY')
    for account_name in account_names:
        department_ids = tuple({department.id for department in departments if
                                department.account_name == account_name})
        cookies = redis_db.get_cookies(account_name)
        stop_sales = await SectorStopSales(cookies, department_ids, today, today).get_data()
        for stop_sale in stop_sales:
            if stop_sale.renewer_name is not None:
                continue
            logger.debug(f'new sector stop sale {stop_sale.department} {stop_sale.sector}')
            serializer = serializers.SectorStopSaleSerializer(stop_sale)
            redis_db.add_report_notification_to_queue(serializer.as_json())


async def run_street_stop_sales():
    departments = db.Department.select()
    account_names = {department.account_name for department in departments}
    today = time_utils.get_now_datetime().format('DD.MM.YYYY')
    for account_name in account_names:
        department_ids = tuple({department.id for department in departments if
                                department.account_name == account_name})
        cookies = redis_db.get_cookies(account_name)
        stop_sales = await StreetStopSales(cookies, department_ids, today, today).get_data()
        for stop_sale in stop_sales:
            if stop_sale.renewer_name is not None:
                continue
            logger.debug(f'new street stop sale {stop_sale.department} {stop_sale.sector}')
            serializer = serializers.StreetStopSaleSerializer(stop_sale)
            redis_db.add_report_notification_to_queue(serializer.as_json())
