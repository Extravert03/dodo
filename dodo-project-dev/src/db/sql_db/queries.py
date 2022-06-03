import traceback
from typing import Iterable

import peewee

from db.sql_db.engine import db_engine
from db.sql_db.models import (
    Department,
    DepartmentRegion,
    DeliveryStatistics,
    DetailedDeliveryStatistics,
    KitchenStatistics,
    RevenueStatistics,
    BeingLateCertificatesStatistics,
    TelegramChat,
    ReportType,
    ForwardingReport,
    OrdersStatistics,
)


def add_department(department_id: int, name: str, account_name: str, region: DepartmentRegion):
    department = Department.create(id=department_id, name=name, account_name=account_name,
                                   region=region)
    with db_engine.atomic() as transaction:
        try:
            DetailedDeliveryStatistics.create(department=department)
            DeliveryStatistics.create(department=department)
            KitchenStatistics.create(department=department)
            RevenueStatistics.create(department=department)
            BeingLateCertificatesStatistics.create(department=department),
            OrdersStatistics.create(department=department),
        except peewee.DatabaseError:
            traceback.print_exc()
            transaction.rollback()
            department.delete()
        else:
            transaction.commit()


def get_report_type_by_id(report_type_id: int) -> ReportType:
    return ReportType.get_by_id(report_type_id)


def get_department_by_id(department_id: int) -> Department:
    return Department.get_by_id(department_id)


def get_or_create_telegram_chat_by_chat_id(chat_id: int) -> TelegramChat:
    return TelegramChat.get_or_create(chat_id=chat_id)[0]


def get_already_added_departments(chat_id: int, report_type_id: int) -> Iterable[ForwardingReport]:
    report_type = get_report_type_by_id(report_type_id)
    telegram_chat = get_or_create_telegram_chat_by_chat_id(chat_id)
    return ForwardingReport.select().where(
        (ForwardingReport.report_type == report_type)
        & (ForwardingReport.telegram_chat == telegram_chat)
    ).execute()


def get_departments_by_region_id(region_id: int) -> Iterable[Department]:
    return Department.select().join(DepartmentRegion).where(
        Department.region.id == region_id).execute()


def add_forwarding_report_department(chat_id: int, report_type_id: int, department_id: int) -> \
        tuple[ForwardingReport, bool]:
    report_type = get_report_type_by_id(report_type_id)
    telegram_chat = get_or_create_telegram_chat_by_chat_id(chat_id)
    department = get_department_by_id(department_id)
    return ForwardingReport.get_or_create(report_type=report_type, telegram_chat=telegram_chat,
                                          department=department)


def add_batch_all_departments(chat_id: int, report_type_id: int, region_id: int):
    departments = get_departments_by_region_id(region_id)
    for department in departments:
        add_forwarding_report_department(chat_id, report_type_id, department.id)


def disable_batch_all_departments(chat_id: int, report_type_id: int):
    added_departments = get_already_added_departments(chat_id, report_type_id)
    for added_department in added_departments:
        added_department.delete_instance()


def get_current_chat_forwarding_reports(chat_id: int) -> Iterable[ForwardingReport]:
    report_type = ReportType.get(name='Отчёты по статистике')
    telegram_chat = get_or_create_telegram_chat_by_chat_id(chat_id)
    return ForwardingReport.select().where(
        ForwardingReport.report_type == report_type,
        ForwardingReport.telegram_chat == telegram_chat).execute()


def get_department_by_name(name: str) -> Department:
    return Department.get(name=name.lower())


def get_telegram_chats_by_department_name_and_report_type(
        department_name: str, report_type: ReportType) -> list[TelegramChat]:
    department = get_department_by_name(department_name)
    forwarding_reports = (ForwardingReport.select().join(TelegramChat)
                          .where(ForwardingReport.department == department,
                                 ForwardingReport.report_type == report_type).execute())
    return [forwarding_report.telegram_chat for forwarding_report in forwarding_reports]


def get_telegram_chats_for_canceled_orders_reports(department_name: str) -> list[TelegramChat]:
    report_type = ReportType.get(name='Отмены заказов')
    return get_telegram_chats_by_department_name_and_report_type(department_name, report_type)


def get_telegram_chats_for_ingredient_stop_sales(department_name: str) -> list[TelegramChat]:
    report_type = ReportType.get(name='Стопы-возобновления')
    return get_telegram_chats_by_department_name_and_report_type(department_name, report_type)


def get_telegram_chats_for_pizzeria_stop_sales(department_name: str) -> list[TelegramChat]:
    report_type = ReportType.get(name='Стопы (Пиццерия)')
    return get_telegram_chats_by_department_name_and_report_type(department_name, report_type)


def get_telegram_chats_for_ingredients_stop_sales(department_name: str) -> list[TelegramChat]:
    report_type = ReportType.get(name='Стопы (Ингредиент)')
    return get_telegram_chats_by_department_name_and_report_type(department_name, report_type)


def get_telegram_chats_for_sector_stop_sales(department_name: str) -> list[TelegramChat]:
    report_type = ReportType.get(name='Стопы (Сектор)')
    return get_telegram_chats_by_department_name_and_report_type(department_name, report_type)


def get_telegram_chats_for_street_stop_sales(department_name: str) -> list[TelegramChat]:
    report_type = ReportType.get(name='Стопы (Улица)')
    return get_telegram_chats_by_department_name_and_report_type(department_name, report_type)
