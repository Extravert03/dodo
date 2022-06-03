import time

import db
from db import redis_db
from dodo_api import serializers
from dodo_api.models import (
    CanceledOrderReport,
    IngredientStopSale,
    PizzeriaStopSaleReport,
    IngredientStopSaleReport,
    SectorStopSaleReport,
    StreetStopSaleReport,
)
from dodo_api.utils import time_utils
from reports_notifier_service import telegram


def send_canceled_order_notification(report_notification: CanceledOrderReport):
    telegram_chats = db.get_telegram_chats_for_canceled_orders_reports(report_notification.department)
    chat_ids = {chat.chat_id for chat in telegram_chats}
    order_lifetime = (
                report_notification.receipt_printed_at - report_notification.order_created_at).in_minutes()
    text = (f'{report_notification.department.title()}'
            f' отменён заказ <a href="https://shiftmanager.dodopizza.ru/Managment/ShiftManagment/'
            f'Order?orderUUId={report_notification.order_uuid}">№{report_notification.order_no}</a>'
            f' в {report_notification.order_price}р\n'
            f'Тип заказа: {report_notification.order_type}\n'
            f'Заказ сделан в {report_notification.order_created_at.format("HH:mm")},'
            f' отменён в {report_notification.receipt_printed_at.format("HH:mm")}\n'
            f'Между заказом и отменой прошло {order_lifetime} минут')
    for chat_id in chat_ids:
        telegram.send_message(chat_id, text)


def send_ingredient_stop_sale_report_notification(report_notification: IngredientStopSale):
    telegram_chats = db.get_telegram_chats_for_ingredient_stop_sales(report_notification.sale_point_name)
    chat_ids = {chat.chat_id for chat in telegram_chats}
    lines = [
        f'<b>{"Остановка" if report_notification.action == "stop" else "Возобновление"} продаж</b>',
        f'Точка продаж: {report_notification.sale_point_name.capitalize()}',
        f'Продукт: {report_notification.product}',
        f'Кто {"остановил" if report_notification.action == "stop" else "возобновил"}:'
        f' {report_notification.employee}',
    ]
    if report_notification.date:
        lines.append(f'Дата {"остановки" if report_notification.action == "stop" else "возобновления"}:'
                     f' {report_notification.date}')
    for chat_id in chat_ids:
        telegram.send_message(chat_id, '\n'.join(lines))


def send_pizzeria_stop_sale_report_notification(report_notification: PizzeriaStopSaleReport):
    telegram_chats = db.get_telegram_chats_for_pizzeria_stop_sales(report_notification.department)
    chat_ids = {chat.chat_id for chat in telegram_chats}
    stop_duration = (time_utils.get_now_datetime() - report_notification.stopped_at).in_minutes()
    if stop_duration >= 30:
        text = [f'❗️ {report_notification.department} в стопе {stop_duration} минут'
                f' с ({report_notification.stopped_at.format("HH:mm")}) ❗️\n']
    else:
        text = [f'{report_notification.department} в стопе {stop_duration} минут'
                f' с ({report_notification.stopped_at.format("HH:mm")})\n']
    text.append(f'Причина остановки: {report_notification.stop_reason}\n'
                f'{report_notification.stop_type}\n'
                f'Тип продажи: {report_notification.sale_type}')
    for chat_id in chat_ids:
        telegram.send_message(chat_id, ''.join(text))


def send_ingredients_stop_sale_report_notification(report_notification: IngredientStopSaleReport):
    telegram_chats = db.get_telegram_chats_for_ingredients_stop_sales(report_notification.department)
    chat_ids = {chat.chat_id for chat in telegram_chats}
    stop_duration = (time_utils.get_now_datetime() - report_notification.stopped_at).in_minutes()
    if stop_duration >= 30:
        text = [f'❗️ {report_notification.department.capitalize()} в стопе {stop_duration} минут'
                f' с ({report_notification.stopped_at.format("HH:mm")}) ❗️\n']
    else:
        text = [f'{report_notification.department} в стопе {stop_duration} минут'
                f' с ({report_notification.stopped_at.format("HH:mm")})\n']
    text.append(f'Ингредиент: {report_notification.ingredient}')
    for chat_id in chat_ids:
        telegram.send_message(chat_id, ''.join(text))


def send_sector_stop_sale_report_notification(report_notification: SectorStopSaleReport):
    telegram_chats = db.get_telegram_chats_for_sector_stop_sales(report_notification.department)
    chat_ids = {chat.chat_id for chat in telegram_chats}
    stop_duration = (time_utils.get_now_datetime() - report_notification.stopped_at).in_minutes()
    if stop_duration >= 30:
        text = [f'❗️ {report_notification.department.capitalize()} в стопе {stop_duration} минут'
                f' с ({report_notification.stopped_at.format("HH:mm")}) ❗️\n']
    else:
        text = [f'{report_notification.department} в стопе {stop_duration} минут'
                f' с ({report_notification.stopped_at.format("HH:mm")})\n']
    text.append(f'Сектор: {report_notification.sector}')
    for chat_id in chat_ids:
        telegram.send_message(chat_id, ''.join(text))


def send_street_stop_sale_report_notification(report_notification: StreetStopSaleReport):
    telegram_chats = db.get_telegram_chats_for_street_stop_sales(report_notification.department)
    chat_ids = {chat.chat_id for chat in telegram_chats}
    stop_duration = (time_utils.get_now_datetime() - report_notification.stopped_at).in_minutes()
    if stop_duration >= 30:
        text = [f'❗️ {report_notification.department.capitalize()} в стопе {stop_duration} минут'
                f' с ({report_notification.stopped_at.format("HH:mm")}) ❗️\n']
    else:
        text = [f'{report_notification.department} в стопе {stop_duration} минут'
                f' с ({report_notification.stopped_at.format("HH:mm")})\n']
    text.append(f'Улица: {report_notification.street}')
    for chat_id in chat_ids:
        telegram.send_message(chat_id, ''.join(text))


notification_types_map = {
    'canceled_order': send_canceled_order_notification,
}

serializers_map = [
    {
        'serializer': serializers.CanceledOrderReportSerializer,
        'send_report_callback': send_canceled_order_notification,
    },
    {
        'serializer': serializers.IngredientStopSaleSerializer,
        'send_report_callback': send_ingredient_stop_sale_report_notification,
    },
    {
        'serializer': serializers.PizzeriaStopSaleSerializer,
        'send_report_callback': send_pizzeria_stop_sale_report_notification,
    },
    {
        'serializer': serializers.IngredientsStopSaleSerializer,
        'send_report_callback': send_ingredients_stop_sale_report_notification,
    },
    {
        'serializer': serializers.StreetStopSaleSerializer,
        'send_report_callback': send_street_stop_sale_report_notification,
    },
    {
        'serializer': serializers.SectorStopSaleSerializer,
        'send_report_callback': send_sector_stop_sale_report_notification,
    },
]


def run_notifier_service():
    while True:
        report_notification = redis_db.get_report_notification_from_queue()
        if report_notification is None:
            time.sleep(1)
            continue
        for serializer_tools in serializers_map:
            serializer = serializer_tools['serializer']
            callback = serializer_tools['send_report_callback']
            if serializer.is_correct_serializer(report_notification):
                callback(serializer(report_notification).as_python())
                break
        time.sleep(1)
